"""
Generate per-client tape-list queries by extracting them from the source
Production Tape Review .sql files and writing one file per client into
DHT_Dashboard/file_load_queries/, plus servers.json mapping each
DatabaseName to its ETL server.

Originally a one-shot at build time; kept here for re-running when new
clients are added to the source folders or existing client queries change.
Edits to individual `.sql` files in file_load_queries/ after a migration
will be overwritten if the script is re-run.

Usage:  py scripts/migrate_file_load_queries.py
"""
import os
import re
import json

SRC_DIRS = [
    r"C:\Users\gw0\TapeReviewQueries\Production Tape Review - Medical Clients",
    r"C:\Users\gw0\TapeReviewQueries\Production Tape Review - Rx Clients",
]
DEST_DIR = r"C:\Users\gw0\DHT_Dashboard\file_load_queries"


def server_from_filename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    m = re.search(r"-\s*(ETL\d|CM9)\s*$", base, re.IGNORECASE)
    if not m:
        return None
    tag = m.group(1).upper()
    return "TRGCM9" if tag == "CM9" else "TRG" + tag


def add_top_limit(query, limit=200):
    if re.search(r"\bSELECT\s+TOP\b", query, re.IGNORECASE):
        return query
    return re.sub(r"\bSELECT\b", f"SELECT TOP {limit}", query, count=1, flags=re.IGNORECASE)


def extract_tape_queries(sql_text):
    """Return [(db_name, query)] for each SELECT block that looks like a tape-list query."""
    results = []
    positions = [m.start() for m in re.finditer(r"(?m)^\s*SELECT\b", sql_text, re.IGNORECASE)]

    for i, pos in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(sql_text)
        block = sql_text[pos:end].strip()

        # Must reference a tape-like table in the FROM clause.
        # tblFileLoad is used by a small number of clients in place of tape/tblTape.
        from_match = re.search(
            r"FROM\s+\[?(\w+)\]?\.\[?\w+\]?\.\[?(tape|tblTape|tblFileLoad)\]?",
            block,
            re.IGNORECASE,
        )
        if not from_match:
            continue

        # Tape-list queries either JOIN to a file-type config table or have ORDER BY.
        # Bare ad-hoc lookups (WHERE TapeID = X, WHERE ProdCtrlNo IN (...)) have neither.
        has_join = bool(re.search(r"\bJOIN\b", block, re.IGNORECASE))
        has_order = bool(re.search(r"\bORDER\s+BY\b", block, re.IGNORECASE))
        if not has_join and not has_order:
            continue

        db_name = from_match.group(1)
        results.append((db_name, add_top_limit(block)))

    return results


os.makedirs(DEST_DIR, exist_ok=True)

servers = {}
written = []
skipped = []
conflicts = []

for src_dir in SRC_DIRS:
    for fname in sorted(os.listdir(src_dir)):
        if not fname.lower().endswith(".sql"):
            skipped.append(fname)
            continue

        server = server_from_filename(fname)
        if not server:
            skipped.append(f"{fname} (no server in filename)")
            continue

        filepath = os.path.join(src_dir, fname)
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            sql_text = f.read()

        queries = extract_tape_queries(sql_text)
        if not queries:
            skipped.append(f"{fname} (no tape queries found)")
            continue

        for db_name, query in queries:
            if db_name in servers and servers[db_name] != server:
                conflicts.append(f"{db_name}: already mapped to {servers[db_name]}, now seeing {server}")
            servers[db_name] = server

            dest = os.path.join(DEST_DIR, f"{db_name}.sql")
            with open(dest, "w", encoding="utf-8") as f:
                f.write(query)
            written.append(f"{db_name:30s} -> {server}  (from {fname})")

with open(os.path.join(DEST_DIR, "servers.json"), "w", encoding="utf-8") as f:
    json.dump(servers, f, indent=2, sort_keys=True)

print(f"Written {len(written)} client files:\n")
for w in sorted(written):
    print(f"  {w}")

if skipped:
    print(f"\nSkipped {len(skipped)}:")
    for s in skipped:
        print(f"  {s}")

if conflicts:
    print(f"\nCONFLICTS (need manual review):")
    for c in conflicts:
        print(f"  {c}")

print(f"\nservers.json written with {len(servers)} entries.")
