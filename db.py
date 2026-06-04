import os
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import pyodbc

_BACKSWEEP_DATE_RANGE_RE = re.compile(r"\d{4}-\d{2}-\d{2}_\d{4}-\d{2}-\d{2}")

CONN_STR = os.environ.get("DHT_CONN_STR") or (
    "DRIVER={SQL Server};"
    "SERVER=TRGUTIL10;"
    "DATABASE=DHTStats;"
    "Trusted_Connection=yes;"
)

# ── Kaiser aggregation ─────────────────────────────────────────────────────
# Kaiser delivers a single ADO ticket ("Kaiser - SNAP/MINE") covering the
# feeds below. Kaiser_WA and KaiserWARRx have their own delivery tickets and
# are intentionally NOT included here — they stay as their own dropdown
# entries with the normal RAMP/ADO flow.
KAISER_AGGREGATE_NAME = "Kaiser"
KAISER_WEEKLY_DATABASES = [
    "Kaiser_CO",
    "Kaiser_GA",
    "Kaiser_HI",
    "Kaiser_MASTapestry",
    "Kaiser_NW",
    "KaiserNCPareo",
    "KaiserSCPareo",
]
KAISER_AMBULANCE_DATABASES = [
    "KaiserAmbCO",
    "KaiserAmbGA",
    "KaiserAmbHI",
    "Kaiser_AmbM",
    "KaiserAmbN",
    "KaiserAmbNW",
    "Kaiser_AmbS",
]
KAISER_AGGREGATE_DATABASES = KAISER_WEEKLY_DATABASES + KAISER_AMBULANCE_DATABASES

# Kaiser weekly feeds whose mining files don't carry the standard claim
# TypeIDs (1, 7, 100, 110, 1000). For these, the Claims File column matches
# on filename containing CLM_HDR or CLM_DTL instead — verified live:
# Kaiser_CO files are TypeID=6 named like '20260505_CO_P_CLM_DTL.csv'.
# KaiserNCPareo and KaiserSCPareo use TypeID=1000 with 'Claim_YYYY-MM-DD'
# filenames and work on the standard filter. The 7 monthly ambulance feeds
# use TypeID 1/1000 with 'XX_AMB_DATA_PAID - YYYY-MM.txt' filenames, also
# caught by the standard filter — both groups are intentionally excluded.
KAISER_CLM_HDR_DTL_DATABASES = [
    db_name for db_name in KAISER_WEEKLY_DATABASES
    if db_name not in ("KaiserNCPareo", "KaiserSCPareo")
]


def kaiser_delivery_week(now=None):
    """Return (start, anchor_wed, end) for the active Kaiser delivery cycle.

    Delivery cadence: snap Wednesday, deliver Thursday. The "active" cycle
    runs Thu 00:00 through the following Wed 23:59:59. When called on a
    Wednesday the anchor is today; on Thursday it rolls forward to the next
    Wednesday so the new cycle's loads start populating.
    """
    now = now or datetime.now()
    days_until_wed = (2 - now.weekday()) % 7  # weekday(): Mon=0..Sun=6; Wed=2
    anchor_wed = (now + timedelta(days=days_until_wed)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start = anchor_wed - timedelta(days=6)            # Thu 00:00
    end = anchor_wed + timedelta(days=1)              # next Thu 00:00 (exclusive)
    return start, anchor_wed, end


def _query(sql, *params):
    conn = pyodbc.connect(CONN_STR)
    try:
        cursor = conn.execute(sql, *params) if params else conn.execute(sql)
        cols = [col[0] for col in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_active_client_names():
    sql = """
        SELECT DISTINCT c.DatabaseName
        FROM DHT.Certification c
        WHERE c.CurrentStatus IN ('Email sent, Ready for Certification review', 'Certified')
          AND c.AlertTimestamp >= DATEADD(day, -60, GETDATE())
          AND EXISTS (
              SELECT 1 FROM DHT.TableList tl
              WHERE tl.CertID = c.ID
                AND tl.Name LIKE '%Mining%'
          )
        ORDER BY c.DatabaseName
    """
    raw = [row["DatabaseName"] for row in _query(sql)]
    kaiser_present = any(name in KAISER_AGGREGATE_DATABASES for name in raw)
    out = [name for name in raw if name not in KAISER_AGGREGATE_DATABASES]
    if kaiser_present:
        out.append(KAISER_AGGREGATE_NAME)
        out.sort()
    return out


def get_active_certs(database_name):
    if database_name == KAISER_AGGREGATE_NAME:
        db_filter = KAISER_AGGREGATE_DATABASES
    else:
        db_filter = [database_name]

    placeholders = ", ".join("?" * len(db_filter))
    sql = f"""
        SELECT
            c.ID                            AS CertID,
            c.DatabaseName,
            c.CertLevel,
            c.AlertTimestamp,
            c.ThresholdCount,
            c.Comment,
            c.CurrentStatus,
            ISNULL(cfg.Value, '0')          AS isPharmacy,
            (SELECT COUNT(*)
             FROM   dbo.tblDHComments dc
             WHERE  dc.DatabaseName = c.DatabaseName
               AND  dc.TimeStamp   >= c.AlertTimestamp) AS RecentCommentCount
        FROM DHT.Certification c
        LEFT JOIN config.Configuration cfg
            ON  cfg.DatabaseName = c.DatabaseName
            AND cfg.Name         = 'isPharmacy'
        WHERE c.CurrentStatus IN ('Email sent, Ready for Certification review', 'Certified')
          AND c.AlertTimestamp >= DATEADD(day, -60, GETDATE())
          AND c.DatabaseName IN ({placeholders})
          AND EXISTS (
              SELECT 1 FROM DHT.TableList tl
              WHERE tl.CertID = c.ID
                AND tl.Name LIKE '%Mining%'
          )
          AND NOT EXISTS (
              SELECT 1 FROM DHT.TableList tl2
              WHERE tl2.CertID = c.ID
                AND tl2.CurrentStatus IN ('Chimera - Ready for Stats', 'Removed')
          )
        ORDER BY
            CASE WHEN c.CurrentStatus = 'Email sent, Ready for Certification review' THEN 0 ELSE 1 END,
            c.AlertTimestamp DESC
    """
    return _query(sql, *db_filter)


def get_cert_claim_names(cert_ids):
    """Return {cert_id: [FileName, ...]} from RAMP.etl.Tape for claims (Mining) files.

    Most clients identify claims files via TypeID IN (1, 7, 100, 110, 1000).
    Kaiser feeds listed in KAISER_CLM_HDR_DTL_DATABASES deliver their claims
    with TypeIDs outside that set (e.g. Kaiser_CO uses TypeID=6 with
    CLM_DTL filenames), so for those feeds we match on filename containing
    CLM_HDR or CLM_DTL instead.
    """
    if not cert_ids:
        return {}
    placeholders = ", ".join("?" * len(cert_ids))
    kaiser_placeholders = ", ".join("?" * len(KAISER_CLM_HDR_DTL_DATABASES))
    sql = f"""
        SELECT DISTINCT tl.CertID, t.FileName
        FROM DHT.TableList tl
        JOIN DHT.Certification c ON c.ID = tl.CertID
        JOIN RAMP.etl.Tape t ON t.TapeID = tl.TapeID AND t.DBName = c.DatabaseName
        WHERE tl.CertID IN ({placeholders})
          AND tl.Name LIKE '%Mining%'
          AND (
                (c.DatabaseName IN ({kaiser_placeholders})
                 AND (t.FileName LIKE '%CLM_HDR%' OR t.FileName LIKE '%CLM_DTL%'))
             OR (c.DatabaseName NOT IN ({kaiser_placeholders})
                 AND t.TypeID IN (1, 7, 100, 110, 1000))
          )
        ORDER BY tl.CertID, t.FileName
    """
    params = list(cert_ids) + KAISER_CLM_HDR_DTL_DATABASES + KAISER_CLM_HDR_DTL_DATABASES
    result = {}
    for row in _query(sql, *params):
        result.setdefault(row["CertID"], []).append(row["FileName"])
    return result


def get_cert_pcns(cert_ids):
    """Return {cert_id: [pcn, ...]} for the given list of cert IDs."""
    if not cert_ids:
        return {}
    placeholders = ", ".join("?" * len(cert_ids))
    sql = f"""
        SELECT DISTINCT CertID, PCN
        FROM DHT.TableList
        WHERE CertID IN ({placeholders})
          AND PCN IS NOT NULL
        ORDER BY CertID, PCN
    """
    result = {}
    for row in _query(sql, *cert_ids):
        result.setdefault(row["CertID"], []).append(row["PCN"])
    return result


def get_cert(cert_id):
    sql = """
        SELECT
            c.ID                            AS CertID,
            c.DatabaseName,
            c.CertLevel,
            c.CertSet,
            c.AlertTimestamp,
            c.ThresholdCount,
            c.Comment,
            c.CurrentStatus,
            c.GlobalNotificationFlag,
            c.AuditTargetNotificationFlag,
            c.SubroTargetNotificationFlag,
            c.RxTargetNotificationFlag,
            ISNULL(cfg.Value, '0')          AS isPharmacy
        FROM DHT.Certification c
        LEFT JOIN config.Configuration cfg
            ON  cfg.DatabaseName = c.DatabaseName
            AND cfg.Name         = 'isPharmacy'
        WHERE c.ID = ?
    """
    rows = _query(sql, cert_id)
    return rows[0] if rows else None


def get_cert_tables(cert_id):
    sql = """
        SELECT
            ID, Name, PCN, TapeID, FileTypeID,
            CurrentStatus, StatTimestamp, ValidationTimestamp,
            Comment, isActive
        FROM DHT.TableList
        WHERE CertID = ?
        ORDER BY Name
    """
    return _query(sql, cert_id)


def get_cert_issues(cert_id):
    sql = """
        SELECT
            v.ValidationLevel,
            v.ValidationSet,
            v.FileTypeID,
            f.Name                  AS FieldName,
            v.Value,
            v.Percentage,
            v.ZScore,
            v.Determination,
            v.ValidationAverage,
            v.ValidationDeviation,
            v.WeightedDetermination,
            v.Comment
        FROM DHT.Validation v
        JOIN config.ClientField cf ON cf.ID  = v.ClientFieldID
        JOIN config.Field        f  ON f.ID  = cf.FieldID
        WHERE v.CertID      = ?
          AND v.Determination != 0
        ORDER BY ABS(v.ZScore) DESC
    """
    return _query(sql, cert_id)


def get_cert_claim_tapeids(cert_id):
    """Return list of TapeIDs for mining files in this cert."""
    sql = """
        SELECT DISTINCT TapeID
        FROM DHT.TableList
        WHERE CertID = ?
          AND Name LIKE '%Mining%'
          AND TapeID IS NOT NULL
        ORDER BY TapeID
    """
    return [row["TapeID"] for row in _query(sql, cert_id)]


def get_pcn_stats(database_name, cert_id):
    sql = """
        SELECT ps.PCN, ps.MinPaidDate, ps.MaxPaidDate, ps.GrossDollars, ps.RecordCount
        FROM rpt.vwSelectPCNStats ps
        WHERE ps.DatabaseName = ?
          AND ps.PCN IN (
              SELECT DISTINCT PCN
              FROM   DHT.TableList
              WHERE  CertID = ?
                AND  PCN IS NOT NULL
          )
        ORDER BY ps.PCN
    """
    return _query(sql, database_name, cert_id)


def add_comment(database_name, pcn, tape_id, category, tfs, comment):
    sql = """
        INSERT INTO dbo.tblDHComments
            (DatabaseName, PCN, TapeID, TimeStamp, Category, TFS, Comment)
        VALUES (?, ?, ?, GETDATE(), ?, ?, ?)
    """
    conn = pyodbc.connect(CONN_STR)
    try:
        conn.execute(
            sql,
            database_name,
            int(pcn) if pcn else None,
            int(tape_id) if tape_id else None,
            category or None,
            tfs or None,
            comment,
        )
        conn.commit()
    finally:
        conn.close()


def get_same_month_cert_history(database_name, exclude_cert_id, month, year, limit=5):
    """
    Return up to N certified deliveries from the same calendar month in prior years,
    with per-field validation detail attached as Issues. `year` is the current cert's
    year; certs from that year and later are excluded so the result is strictly
    prior-year same-month history.
    """
    cert_sql = """
        SELECT TOP (?)
            c.ID            AS CertID,
            c.AlertTimestamp,
            c.ThresholdCount,
            c.CertLevel
        FROM DHT.Certification c
        WHERE c.DatabaseName = ?
          AND c.CurrentStatus = 'Certified'
          AND c.ID != ?
          AND MONTH(c.AlertTimestamp) = ?
          AND YEAR(c.AlertTimestamp) < ?
          AND EXISTS (
              SELECT 1 FROM DHT.TableList tl
              WHERE tl.CertID = c.ID
                AND tl.Name LIKE '%Mining%'
          )
          AND NOT EXISTS (
              SELECT 1 FROM DHT.TableList tl2
              WHERE tl2.CertID = c.ID
                AND tl2.CurrentStatus IN ('Chimera - Ready for Stats', 'Removed')
          )
        ORDER BY c.AlertTimestamp DESC
    """
    certs = _query(cert_sql, limit, database_name, exclude_cert_id, month, year)
    if not certs:
        return []

    cert_ids = [c["CertID"] for c in certs]
    placeholders = ", ".join("?" * len(cert_ids))
    field_sql = f"""
        SELECT v.CertID, f.Name AS FieldName, v.Determination
        FROM DHT.Validation v
        JOIN config.ClientField cf ON cf.ID = v.ClientFieldID
        JOIN config.Field f        ON f.ID  = cf.FieldID
        WHERE v.CertID IN ({placeholders})
          AND v.Determination != 0
    """
    field_rows = _query(field_sql, *cert_ids)

    issues_by_cert = {}
    for row in field_rows:
        issues_by_cert.setdefault(row["CertID"], []).append({
            "FieldName": row["FieldName"],
            "Determination": row["Determination"],
        })

    for c in certs:
        c["Issues"] = issues_by_cert.get(c["CertID"], [])

    return certs


def get_cert_backsweep_files(cert_id):
    """Return mining files on this cert that look like backsweep deliveries.

    Two detection signals:
      - Filename contains a `YYYY-MM-DD_YYYY-MM-DD` date-range token
        (clients with this naming convention spell out the data period).
      - File size is materially larger than the recent median for the same
        client (> 2.5× median), excluding this cert's own files.

    Returns a list of dicts: {FileName, Size, TapeID, Reasons}.
    """
    files_sql = """
        SELECT t.FileName, t.Size, t.TapeId AS TapeID, c.DatabaseName
        FROM DHT.TableList tl
        JOIN DHT.Certification c ON c.ID = tl.CertID
        JOIN RAMP.etl.Tape t  ON t.TapeID = tl.TapeID AND t.DBName = c.DatabaseName
        WHERE tl.CertID = ?
          AND tl.Name LIKE '%Mining%'
          AND t.TypeId IN (1, 7, 100, 110, 1000)
    """
    cert_files = _query(files_sql, cert_id)
    if not cert_files:
        return []

    db_name = cert_files[0]["DatabaseName"]

    sizes_sql = """
        SELECT TOP 100 t.Size
        FROM RAMP.etl.Tape t
        WHERE t.DBName = ?
          AND t.TypeId IN (1, 7, 100, 110, 1000)
          AND t.Size > 0
          AND t.TapeID NOT IN (
              SELECT TapeID FROM DHT.TableList WHERE CertID = ? AND TapeID IS NOT NULL
          )
        ORDER BY t.DateLoaded DESC
    """
    recent_sizes = sorted(r["Size"] for r in _query(sizes_sql, db_name, cert_id))
    median = recent_sizes[len(recent_sizes) // 2] if recent_sizes else 0
    size_threshold = median * 2.5 if median else None

    flagged = []
    for f in cert_files:
        reasons = []
        if _BACKSWEEP_DATE_RANGE_RE.search(f["FileName"] or ""):
            reasons.append("date-range in filename")
        if size_threshold and f["Size"] and f["Size"] > size_threshold:
            reasons.append(f"size {f['Size'] / median:.1f}× recent median")
        if reasons:
            flagged.append({
                "FileName": f["FileName"],
                "Size": f["Size"],
                "TapeID": f["TapeID"],
                "Reasons": reasons,
            })
    return flagged


def get_cert_claim_file_size(cert_id):
    """Total mining claim-file size (bytes) for a cert. Returns None when no
    matching files are loaded yet."""
    sql = """
        SELECT SUM(CAST(t.Size AS BIGINT)) AS TotalSize
        FROM DHT.Certification c
        JOIN DHT.TableList tl ON tl.CertID = c.ID AND tl.Name LIKE '%Mining%'
        JOIN RAMP.etl.Tape t  ON t.TapeID = tl.TapeID AND t.DBName = c.DatabaseName
        WHERE c.ID = ?
          AND t.TypeId IN (1, 7, 100, 110, 1000)
    """
    rows = _query(sql, cert_id)
    return rows[0]["TotalSize"] if rows and rows[0]["TotalSize"] is not None else None


def get_recent_claim_file_sizes(database_name, exclude_cert_id, limit=15):
    """Total mining claim-file sizes (bytes) for the most recent N certified
    deliveries — used to derive a baseline for EOM/SOM detection."""
    sql = """
        SELECT TOP (?) SUM(CAST(t.Size AS BIGINT)) AS TotalSize
        FROM DHT.Certification c
        JOIN DHT.TableList tl ON tl.CertID = c.ID AND tl.Name LIKE '%Mining%'
        JOIN RAMP.etl.Tape t  ON t.TapeID = tl.TapeID AND t.DBName = c.DatabaseName
        WHERE c.DatabaseName = ?
          AND c.CurrentStatus = 'Certified'
          AND c.ID != ?
          AND t.TypeId IN (1, 7, 100, 110, 1000)
        GROUP BY c.ID, c.AlertTimestamp
        ORDER BY c.AlertTimestamp DESC
    """
    rows = _query(sql, limit, database_name, exclude_cert_id)
    return [r["TotalSize"] for r in rows if r["TotalSize"] is not None]


def get_recent_dow_cert_history(database_name, exclude_cert_id, weekday, limit=5):
    """
    Return last N certified deliveries that fell on the same weekday,
    with per-field validation detail attached as Issues.
    weekday: Monday=0 ... Sunday=6 (matches Python's datetime.weekday()).
    """
    cert_sql = """
        SELECT TOP (?)
            c.ID            AS CertID,
            c.AlertTimestamp,
            c.ThresholdCount,
            c.CertLevel
        FROM DHT.Certification c
        WHERE c.DatabaseName = ?
          AND c.CurrentStatus = 'Certified'
          AND c.ID != ?
          AND DATEDIFF(day, '1900-01-01', c.AlertTimestamp) % 7 = ?
          AND EXISTS (
              SELECT 1 FROM DHT.TableList tl
              WHERE tl.CertID = c.ID
                AND tl.Name LIKE '%Mining%'
          )
          AND NOT EXISTS (
              SELECT 1 FROM DHT.TableList tl2
              WHERE tl2.CertID = c.ID
                AND tl2.CurrentStatus IN ('Chimera - Ready for Stats', 'Removed')
          )
        ORDER BY c.AlertTimestamp DESC
    """
    certs = _query(cert_sql, limit, database_name, exclude_cert_id, weekday)
    if not certs:
        return []

    cert_ids = [c["CertID"] for c in certs]
    placeholders = ", ".join("?" * len(cert_ids))
    field_sql = f"""
        SELECT v.CertID, f.Name AS FieldName, v.Determination
        FROM DHT.Validation v
        JOIN config.ClientField cf ON cf.ID = v.ClientFieldID
        JOIN config.Field f        ON f.ID  = cf.FieldID
        WHERE v.CertID IN ({placeholders})
          AND v.Determination != 0
    """
    field_rows = _query(field_sql, *cert_ids)

    issues_by_cert = {}
    for row in field_rows:
        issues_by_cert.setdefault(row["CertID"], []).append({
            "FieldName": row["FieldName"],
            "Determination": row["Determination"],
        })

    for c in certs:
        c["Issues"] = issues_by_cert.get(c["CertID"], [])

    return certs


def get_recent_cert_history(database_name, exclude_cert_id, limit=14):
    """
    Return last N certified claims deliveries with per-field validation detail.
    Each row has: CertID, AlertTimestamp, ThresholdCount, CertLevel,
    and Issues — a list of {FieldName, Determination} dicts.
    """
    cert_sql = """
        SELECT TOP (?)
            c.ID            AS CertID,
            c.AlertTimestamp,
            c.ThresholdCount,
            c.CertLevel
        FROM DHT.Certification c
        WHERE c.DatabaseName = ?
          AND c.CurrentStatus = 'Certified'
          AND c.ID != ?
          AND EXISTS (
              SELECT 1 FROM DHT.TableList tl
              WHERE tl.CertID = c.ID
                AND tl.Name LIKE '%Mining%'
          )
          AND NOT EXISTS (
              SELECT 1 FROM DHT.TableList tl2
              WHERE tl2.CertID = c.ID
                AND tl2.CurrentStatus = 'Chimera - Ready for Stats'
          )
        ORDER BY c.AlertTimestamp DESC
    """
    certs = _query(cert_sql, limit, database_name, exclude_cert_id)
    if not certs:
        return []

    cert_ids = [c["CertID"] for c in certs]
    placeholders = ", ".join("?" * len(cert_ids))
    field_sql = f"""
        SELECT v.CertID, f.Name AS FieldName, v.Determination
        FROM DHT.Validation v
        JOIN config.ClientField cf ON cf.ID = v.ClientFieldID
        JOIN config.Field f        ON f.ID  = cf.FieldID
        WHERE v.CertID IN ({placeholders})
          AND v.Determination != 0
    """
    field_rows = _query(field_sql, *cert_ids)

    issues_by_cert = {}
    for row in field_rows:
        issues_by_cert.setdefault(row["CertID"], []).append({
            "FieldName": row["FieldName"],
            "Determination": row["Determination"],
        })

    for c in certs:
        c["Issues"] = issues_by_cert.get(c["CertID"], [])

    return certs


def get_kaiser_weekly_matrix(anchor_wed=None):
    """Build the Kaiser weekly delivery matrix.

    Rows = feeds, columns = the 7 days Thu→Wed of the active delivery cycle.
    Each populated cell carries the cert plus the MAX TrustScore and MAX
    DuplicateLineKey across that cert's Validation rows (multiple file types
    per cert; surfacing the worst value is what the reviewer needs to see).
    Weekly feeds always render; ambulance feeds only appear when at least
    one load landed in the window.
    """
    if anchor_wed is None:
        start, anchor_wed, end = kaiser_delivery_week()
    else:
        anchor_wed = anchor_wed.replace(hour=0, minute=0, second=0, microsecond=0)
        start = anchor_wed - timedelta(days=6)
        end = anchor_wed + timedelta(days=1)

    days = [start.date() + timedelta(days=i) for i in range(7)]

    db_filter = KAISER_AGGREGATE_DATABASES
    placeholders = ", ".join("?" * len(db_filter))
    # Single LEFT JOIN + conditional MAX instead of two correlated subqueries.
    # Trust Score uses ZScore (the at-or-near-zero check is anomaly-based);
    # Duplicate Line Key uses raw Value (it's a count where 0 = clean).
    sql = f"""
        SELECT
            c.ID                AS CertID,
            c.DatabaseName,
            c.AlertTimestamp,
            c.CurrentStatus,
            c.ThresholdCount,
            MAX(CASE WHEN f.Name = 'TrustScore'       THEN CAST(v.ZScore AS FLOAT) END) AS TrustScoreZ,
            MAX(CASE WHEN f.Name = 'DuplicateLineKey' THEN CAST(v.Value  AS FLOAT) END) AS DuplicateLineKey
        FROM DHT.Certification c
        LEFT JOIN DHT.Validation v   ON v.CertID = c.ID
        LEFT JOIN config.ClientField cf ON cf.ID = v.ClientFieldID
        LEFT JOIN config.Field f        ON f.ID  = cf.FieldID
                                       AND f.Name IN ('TrustScore', 'DuplicateLineKey')
        WHERE c.DatabaseName IN ({placeholders})
          AND c.AlertTimestamp >= ?
          AND c.AlertTimestamp <  ?
          AND EXISTS (
              SELECT 1 FROM DHT.TableList tl
              WHERE tl.CertID = c.ID
                AND tl.Name LIKE '%Mining%'
          )
          AND NOT EXISTS (
              SELECT 1 FROM DHT.TableList tl2
              WHERE tl2.CertID = c.ID
                AND tl2.CurrentStatus IN ('Chimera - Ready for Stats', 'Removed')
          )
        GROUP BY c.ID, c.DatabaseName, c.AlertTimestamp, c.CurrentStatus, c.ThresholdCount
        ORDER BY c.DatabaseName, c.AlertTimestamp
    """
    rows = _query(sql, *db_filter, start, end)

    by_db = {}
    for r in rows:
        by_db.setdefault(r["DatabaseName"], []).append(r)

    def _feed_row(db_name):
        loads = by_db.get(db_name, [])
        loads_by_date = {}
        for load in loads:
            # Multiple certs on the same date keep the most recent (rows are
            # AlertTimestamp-ASC, so the later one overwrites).
            loads_by_date[load["AlertTimestamp"].date()] = load
        return {
            "DatabaseName": db_name,
            "loads_by_date": loads_by_date,
            "load_count": len(loads),
        }

    weekly_feeds = [_feed_row(name) for name in KAISER_WEEKLY_DATABASES]
    ambulance_feeds = [
        _feed_row(name) for name in KAISER_AMBULANCE_DATABASES
        if by_db.get(name)
    ]

    return {
        "anchor_wed": anchor_wed,
        "deliver_thu": anchor_wed + timedelta(days=1),
        "start": start,
        "end": end,
        "days": days,
        "weekly_feeds": weekly_feeds,
        "ambulance_feeds": ambulance_feeds,
    }


# ── Kaiser paid-date coverage ──────────────────────────────────────────────
# Kaiser file naming: each claim file's filename starts with the paid date.
#   Pattern A — most feeds: `20260512_CO_P_CLM_DTL.csv` (compact YYYYMMDD)
#   Pattern B — Pareo bundle files: `Claim_2026-05-12` (hyphenated, no ext)
# The leading paid date is what makes coverage detectable: today's load can
# include files for several different paid dates, all at once, out of order.
KAISER_ETL_SERVER = "TRGETL1"
KAISER_COVERAGE_TTL = 300  # seconds — matches RAMP cache

_kaiser_coverage_cache = {"data": None, "fetched_at": 0.0}


def _parse_kaiser_paid_date(filename):
    if not filename:
        return None
    base = filename.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
    m = re.match(r"(\d{8})_", base)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y%m%d").date()
        except ValueError:
            pass
    m = re.search(r"_(\d{4}-\d{2}-\d{2})$", base)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            pass
    return None


def _kaiser_feed_paid_date_counts(database_name):
    """Connect to one Kaiser feed's ETL DB, scan recent claim filenames, and
    return a Counter mapping paid date → file count. Returns an empty Counter
    on connection or query failure (best-effort: a single broken feed should
    not break the whole coverage panel)."""
    conn_str = (
        "DRIVER={SQL Server};"
        f"SERVER={KAISER_ETL_SERVER};"
        f"DATABASE={database_name};"
        "Trusted_Connection=yes;"
    )
    sql = f"""
        SELECT TOP 2000 FileName
        FROM [{database_name}].[etl].[tape] (nolock)
        WHERE FileName LIKE '%CLM%' OR FileName LIKE '%Claim%'
        ORDER BY TapeID DESC
    """
    counts = Counter()
    try:
        conn = pyodbc.connect(conn_str, timeout=30)
        try:
            for row in conn.execute(sql):
                paid = _parse_kaiser_paid_date(row[0])
                if paid:
                    counts[paid] += 1
        finally:
            conn.close()
    except Exception:
        pass
    return counts


def get_kaiser_paid_date_coverage(lookback_days=14, today=None):
    """Per-feed paid-date coverage for the 7 Kaiser weekly feeds.

    For each feed, parses the paid date out of recent claim filenames and
    builds a lookback-window strip + a list of in-range gap dates. Cached
    for KAISER_COVERAGE_TTL seconds; the 7 feeds are queried in parallel.

    Strip cell status:
      covered — file_count > 0
      gap     — d <= latest_paid_date and file_count == 0
      future  — d > latest_paid_date (expected lag, not a problem)
    """
    if today is None:
        now_ts = time.time()
        cached = _kaiser_coverage_cache["data"]
        if cached is not None and now_ts - _kaiser_coverage_cache["fetched_at"] < KAISER_COVERAGE_TTL:
            return cached
    else:
        now_ts = None  # caller supplied a date — bypass cache (testing/back-dating)

    today = today or date.today()
    strip_start = today - timedelta(days=lookback_days - 1)
    strip_dates = [strip_start + timedelta(days=i) for i in range(lookback_days)]

    with ThreadPoolExecutor(max_workers=len(KAISER_WEEKLY_DATABASES)) as ex:
        counts_by_feed = dict(zip(
            KAISER_WEEKLY_DATABASES,
            ex.map(_kaiser_feed_paid_date_counts, KAISER_WEEKLY_DATABASES),
        ))

    feeds = []
    for db_name in KAISER_WEEKLY_DATABASES:
        counts = counts_by_feed.get(db_name) or Counter()
        latest = max(counts.keys()) if counts else None
        lag = (today - latest).days if latest else None

        strip = []
        gap_dates = []
        for d in strip_dates:
            count = counts.get(d, 0)
            if count > 0:
                status = "covered"
            elif latest is not None and d <= latest:
                status = "gap"
                gap_dates.append(d)
            else:
                status = "future"
            strip.append({"date": d, "status": status, "file_count": count})

        feeds.append({
            "DatabaseName": db_name,
            "latest_paid_date": latest,
            "lag_days": lag,
            "gap_dates": gap_dates,
            "strip": strip,
        })

    result = {
        "today": today,
        "lookback_days": lookback_days,
        "feeds": feeds,
    }
    if now_ts is not None:
        _kaiser_coverage_cache["data"] = result
        _kaiser_coverage_cache["fetched_at"] = now_ts
    return result


def get_cert_kaiser_keys(cert_id):
    """Return {'TrustScoreZ': float|None, 'DuplicateLineKey': float|None} for
    a single cert — the two values that drive the Kaiser delivery decision.

    Mirrors the MAX-aggregation used in get_kaiser_weekly_matrix so the same
    worst-value rule applies to the verdict override."""
    sql = """
        SELECT
            MAX(CASE WHEN f.Name = 'TrustScore'       THEN CAST(v.ZScore AS FLOAT) END) AS TrustScoreZ,
            MAX(CASE WHEN f.Name = 'DuplicateLineKey' THEN CAST(v.Value  AS FLOAT) END) AS DuplicateLineKey
        FROM DHT.Validation v
        JOIN config.ClientField cf ON cf.ID = v.ClientFieldID
        JOIN config.Field f        ON f.ID  = cf.FieldID
                                   AND f.Name IN ('TrustScore', 'DuplicateLineKey')
        WHERE v.CertID = ?
    """
    rows = _query(sql, cert_id)
    # Aggregate always returns exactly one row; values are None when no
    # matching Validation rows exist for that field.
    return rows[0] if rows else {"TrustScoreZ": None, "DuplicateLineKey": None}


def get_comments(database_name):
    sql = """
        SELECT TOP 25
            tblDHCommentsID, DatabaseName, PCN, TapeID,
            TimeStamp, Category, TFS, Comment
        FROM dbo.tblDHComments
        WHERE DatabaseName = ?
        ORDER BY TimeStamp DESC
    """
    return _query(sql, database_name)
