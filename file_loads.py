import os
import re
import json
import pyodbc
from datetime import datetime, date

QUERY_DIR = os.environ.get(
    "DHT_QUERY_DIR",
    os.path.join(os.path.dirname(__file__), "file_load_queries"),
)

# How many rows to keep per file type when the per-type wrap is applied. The
# original TOP 200 cap allowed a single chatty file type (e.g. CenteneRx TRR)
# to crowd out all others. With per-type capping, claims + other types stay
# visible. 50 keeps the total row count reasonable for typical clients with
# 4-8 file types.
PER_TYPE_CAP = int(os.environ.get("DHT_PER_TYPE_CAP", "50"))

# Optional comment override in a client's .sql file:
#   -- partition_by: TableName
# Use this when the auto-detect picks the wrong column or the column isn't
# in the auto-detect list.
_PARTITION_BY_RE = re.compile(
    r"^\s*--\s*partition_by\s*:\s*(\w+)\s*$",
    re.MULTILINE | re.IGNORECASE,
)

# File-type column names we look for in the SQL text. Order matters — the
# first match wins. These are the column aliases that appear across the 107
# per-client query files (verified: TableName/TableType in the etl.tape
# schema, FileType in older dbo.tblTape).
_TYPE_COL_CANDIDATES = ("TableName", "TableType", "FileType")


def _load_servers():
    with open(os.path.join(QUERY_DIR, "servers.json"), encoding="utf-8") as f:
        return json.load(f)


def _fmt(v):
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M")
    if isinstance(v, date):
        return v.strftime("%Y-%m-%d")
    return v


def _detect_date_col(sql):
    """Return the load-date column name for this client's tape query."""
    # 1. Explicit column in SELECT list
    select_match = re.match(
        r"SELECT\s+(?:TOP\s+\d+\s+)?(.*?)FROM\b", sql, re.IGNORECASE | re.DOTALL
    )
    if select_match:
        col_list = select_match.group(1)
        if re.search(r"\bFileLoadDate\b", col_list, re.IGNORECASE):
            return "FileLoadDate"
        if re.search(r"\bFileDate\b", col_list, re.IGNORECASE):
            return "FileDate"
    # 2. Column referenced anywhere (catches SELECT * with an existing WHERE clause)
    if re.search(r"\bFileLoadDate\b", sql, re.IGNORECASE):
        return "FileLoadDate"
    if re.search(r"\bFileDate\b", sql, re.IGNORECASE):
        return "FileDate"
    # 3. Infer from table schema for bare SELECT * queries
    if re.search(r"\betl\b\s*\.\s*\[?tape\]?", sql, re.IGNORECASE):
        return "FileLoadDate"   # etl.tape schema
    if re.search(r"\bdbo\b\s*\.\s*\[?tbl[Tt]ape\]?", sql, re.IGNORECASE):
        return "FileDate"       # dbo.tblTape schema
    return None  # Unknown — skip date filter


def _inject_date_filter(sql, date_col):
    """
    Insert 'WHERE/AND {date_col} >= DATEADD(day, -14, ?)' into the SQL
    immediately before the final un-commented ORDER BY clause.
    """
    lines = sql.splitlines()

    # Find the last un-commented ORDER BY line
    order_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("--"):
            continue
        if re.search(r"\bORDER\s+BY\b", line, re.IGNORECASE):
            order_idx = i

    # Determine connector based on whether an active WHERE already exists
    scope = lines[:order_idx] if order_idx is not None else lines
    has_where = any(
        re.search(r"\bWHERE\b", l, re.IGNORECASE)
        for l in scope
        if not l.strip().startswith("--")
    )
    connector = "AND" if has_where else "WHERE"
    clause = f"{connector} {date_col} >= DATEADD(day, -14, ?)"

    if order_idx is not None:
        lines.insert(order_idx, clause)
    else:
        lines.append(clause)

    return "\n".join(lines)


def _detect_type_col(sql):
    """Return the file-type column to PARTITION BY, or None if we can't tell.

    1. Explicit `-- partition_by: ColumnName` comment wins.
    2. Otherwise look for known column aliases in the SELECT list. Restricted
       to the SELECT clause to avoid false matches on JOIN'd table names
       (e.g. Kaiser's `JOIN [config].[FileType] f` referenced the type table,
       not a column).
    """
    m = _PARTITION_BY_RE.search(sql)
    if m:
        return m.group(1)
    select_match = re.search(
        r"\bSELECT\b\s+(?:TOP\s*\(?\s*\d+\s*\)?\s+)?(.*?)\bFROM\b",
        sql,
        re.IGNORECASE | re.DOTALL,
    )
    if not select_match:
        return None
    select_list = select_match.group(1)
    for col in _TYPE_COL_CANDIDATES:
        if re.search(rf"\b{col}\b", select_list, re.IGNORECASE):
            return col
    return None


def _strip_top(sql):
    """Remove `TOP N` (or `TOP (N)`) from the first SELECT so the wrapped
    inner query doesn't pre-truncate before per-type partitioning."""
    return re.sub(
        r"(SELECT)\s+TOP\s*\(?\s*\d+\s*\)?",
        r"\1",
        sql,
        count=1,
        flags=re.IGNORECASE,
    )


def _extract_and_strip_order_by(sql):
    """Return (sql_without_order_by, order_by_clause). Derived tables can't
    have ORDER BY, so we pull it off the inner SQL and reapply at the outer
    level. Handles the common single-line ORDER BY at the end of the file."""
    lines = sql.splitlines()
    order_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("--"):
            continue
        if re.search(r"\bORDER\s+BY\b", line, re.IGNORECASE):
            order_idx = i  # last un-commented ORDER BY wins
    if order_idx is None:
        return sql, None
    order_line = lines[order_idx]
    m = re.search(r"ORDER\s+BY\s+(.+)$", order_line, re.IGNORECASE)
    order_clause = m.group(1).strip().rstrip(";") if m else None
    return "\n".join(lines[:order_idx] + lines[order_idx + 1:]), order_clause


def _wrap_for_per_type_cap(sql, type_col, cap):
    """Wrap a tape-list SQL so each file type returns at most `cap` rows
    (ranked by the original ORDER BY, defaulting to TapeID DESC). Strips
    the inner TOP and ORDER BY because both are illegal in a derived table.
    """
    inner, order_by = _extract_and_strip_order_by(sql)
    inner = _strip_top(inner)
    order_by = order_by or "[TapeID] DESC"
    return f"""
SELECT * FROM (
    SELECT _src.*,
           ROW_NUMBER() OVER (
               PARTITION BY _src.[{type_col}]
               ORDER BY {order_by}
           ) AS _rn
    FROM (
{inner}
    ) _src
) _ranked
WHERE _rn <= {cap}
ORDER BY {order_by}
"""


def get_file_loads(database_name, alert_timestamp=None):
    """
    Return (columns, rows, error).
    (None, None, None)  — no query configured for this client; tab hidden.
    (None, None, str)   — query configured but connection/execution failed.
    (list, list, None)  — success; columns is a list of column name strings.
    """
    servers = _load_servers()
    server = servers.get(database_name)
    if not server:
        return None, None, None

    sql_path = os.path.join(QUERY_DIR, f"{database_name}.sql")
    if not os.path.exists(sql_path):
        return None, None, None

    with open(sql_path, encoding="utf-8") as f:
        sql = f.read()

    params = []
    if alert_timestamp is not None:
        date_col = _detect_date_col(sql)
        if date_col:
            sql = _inject_date_filter(sql, date_col)
            alert_dt = alert_timestamp
            if hasattr(alert_dt, "tzinfo") and alert_dt.tzinfo is not None:
                alert_dt = alert_dt.replace(tzinfo=None)
            params.append(alert_dt)

    # Per-type wrap: when we can detect a file-type column, give each type
    # its own cap instead of a single TOP that one chatty type can dominate
    # (the CenteneRx TRR problem). Falls back to the original SQL when no
    # type column is identifiable.
    type_col = _detect_type_col(sql)
    if type_col:
        sql = _wrap_for_per_type_cap(sql, type_col, PER_TYPE_CAP)

    conn_str = (
        "DRIVER={SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database_name};"
        "Trusted_Connection=yes;"
    )

    try:
        conn = pyodbc.connect(conn_str, timeout=30)
        try:
            cursor = conn.execute(sql, *params) if params else conn.execute(sql)
            # Drop internal ranking column from the displayed result.
            cols = [col[0] for col in cursor.description if not col[0].startswith("_")]
            keep_idx = [i for i, col in enumerate(cursor.description) if not col[0].startswith("_")]
            rows = [
                {cols[j]: _fmt(row[i]) for j, i in enumerate(keep_idx)}
                for row in cursor.fetchall()
            ]
            return cols, rows, None
        finally:
            conn.close()
    except Exception as e:
        return None, None, str(e)
