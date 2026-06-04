import os
import json
import pyodbc

QUERY_DIR = os.environ.get(
    "DHT_QUERY_DIR",
    os.path.join(os.path.dirname(__file__), "file_load_queries"),
)
RX_VERIFY_DIR = os.environ.get(
    "DHT_RX_VERIFY_DIR",
    os.path.join(os.path.dirname(__file__), "rx_verify_queries"),
)


def _load_servers():
    with open(os.path.join(QUERY_DIR, "servers.json"), encoding="utf-8") as f:
        return json.load(f)


def _fetchall(cursor):
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def merge_by_tape(claim_rows, mining_rows):
    """
    Merge claim and mining row lists (both keyed by TapeID) into one entry per tape.
    Returns a list of dicts: TapeID, claim_paid, claim_records, mining_paid, mining_records, match.
    """
    claim_map = {r["TapeID"]: r for r in (claim_rows or [])}
    mining_map = {r["TapeID"]: r for r in (mining_rows or [])}
    all_tapes = sorted(set(list(claim_map) + list(mining_map)))
    result = []
    for tape_id in all_tapes:
        c = claim_map.get(tape_id)
        m = mining_map.get(tape_id)
        result.append({
            "TapeID": tape_id,
            "claim_paid":    c["Paid"]    if c else None,
            "claim_records": c["Records"] if c else None,
            "mining_paid":    m["Paid"]    if m else None,
            "mining_records": m["Records"] if m else None,
            "match": bool(
                c and m
                and c["Paid"] == m["Paid"]
                and c["Records"] == m["Records"]
            ),
        })
    return result


def get_rx_verification(database_name, tape_ids):
    """
    Return (claim_rows, mining_rows, error).
    claim_rows: list of {TapeID, Paid, Records}, or None if no claim query configured.
    mining_rows: list of {TapeID, Paid, Records}, or None on failure / not configured.
    error: descriptive string, or None on success.
    Returns (None, None, None) when no query file exists for this client.
    """
    if not tape_ids:
        return None, None, "No mining tape IDs found for this cert."

    sql_path = os.path.join(RX_VERIFY_DIR, f"{database_name}.sql")
    if not os.path.exists(sql_path):
        return None, None, None

    with open(sql_path, encoding="utf-8") as f:
        content = f.read()

    if "--MINING--" not in content:
        return None, None, "Malformed query file — no --MINING-- marker."

    parts = content.split("--MINING--", 1)
    mining_sql = parts[1].strip()
    claim_sql = None
    if "--CLAIM--" in parts[0]:
        claim_sql = parts[0].split("--CLAIM--", 1)[1].strip()

    servers = _load_servers()
    server = servers.get(database_name)
    if not server:
        return None, None, f"No server configured for {database_name}."

    placeholders = ", ".join("?" * len(tape_ids))
    params = list(tape_ids)

    try:
        conn_str = (
            "DRIVER={SQL Server};"
            f"SERVER={server};"
            f"DATABASE={database_name};"
            "Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str, timeout=30)
        try:
            claim_rows = None
            if claim_sql:
                claim_rows = _fetchall(
                    conn.execute(claim_sql.replace("{TAPEIDS}", placeholders), *params)
                )
            mining_rows = _fetchall(
                conn.execute(mining_sql.replace("{TAPEIDS}", placeholders), *params)
            )
        finally:
            conn.close()

        return claim_rows, mining_rows, None
    except Exception as e:
        return None, None, str(e)
