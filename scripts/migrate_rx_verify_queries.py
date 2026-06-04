"""
Generate per-client Rx verification queries (rx_verify_queries/*.sql) from
the per-client schema mapping below. Each output file has --CLAIM-- and/or
--MINING-- sections with a `{TAPEIDS}` placeholder that rx_verify.py
substitutes at runtime.

Originally a one-shot at build time; kept here for re-running when new
pharmacy clients are added — add the client to the appropriate group below
and re-run. Edits to individual `.sql` files in rx_verify_queries/ after a
migration will be overwritten if the script is re-run.

Usage:  py scripts/migrate_rx_verify_queries.py
"""
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "rx_verify_queries")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _etl_claim(db, schema, table, paid_col):
    return (
        f"SELECT TapeID, FORMAT(Sum({paid_col}),'C','en-US') [Paid], Format(count(*),'N0') [Records]\n"
        f"FROM [{db}].[{schema}].[{table}] (nolock)\n"
        f"WHERE TapeID IN ({{TAPEIDS}})\n"
        f"GROUP BY TapeID\n"
        f"ORDER BY TapeID"
    )


def _etl_mining(db, paid_col="TotalAmountPaid"):
    return (
        f"SELECT TapeID, FORMAT(Sum({paid_col}),'C','en-US') [Paid], Format(count(*),'N0') [Records]\n"
        f"FROM [{db}].[mining].[RxClaim] (nolock)\n"
        f"WHERE TapeID IN ({{TAPEIDS}})\n"
        f"GROUP BY TapeID\n"
        f"ORDER BY TapeID"
    )


def _cm9_mining(db, paid_col="TotalAmountPaid"):
    return (
        f"SELECT TapeID, FORMAT(Sum({paid_col}),'C','en-US') [Paid], Format(count(*),'N0') [Records]\n"
        f"FROM [{db}].[dbo].[RxClaims] (nolock)\n"
        f"WHERE TapeID IN ({{TAPEIDS}})\n"
        f"GROUP BY TapeID\n"
        f"ORDER BY TapeID"
    )


def write_file(db_name, claim_sql, mining_sql):
    parts = []
    if claim_sql:
        parts.append(f"--CLAIM--\n{claim_sql}")
    parts.append(f"--MINING--\n{mining_sql}")
    path = os.path.join(OUTPUT_DIR, f"{db_name}.sql")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts))
    print(f"  {db_name}.sql")


# ── claim.TRGRxClaim + mining.RxClaim (most common) ──────────────────────────
for _db in ["AetnaRx", "CareFirstRx", "CenteneRx", "CignaRx", "EmblemRx",
            "HAPRx", "Kaiser_WARx", "NCStateRx", "OscarRx", "TuftsRx"]:
    write_file(_db,
               _etl_claim(_db, "claim", "TRGRxClaim", "TotalAmountPaid"),
               _etl_mining(_db))

# ── claim.TRGClaim + mining.RxClaim (standard paid col) ──────────────────────
for _db in ["BCBSSCRx", "MedicaDeanRx", "MMOHRx", "PremeraMedAdvRx"]:
    write_file(_db,
               _etl_claim(_db, "claim", "TRGClaim", "TotalAmountPaid"),
               _etl_mining(_db))

# ── cache.TRGCache + mining.RxClaim ──────────────────────────────────────────
for _db in ["AetnaQNXTRx", "CareSourceRx"]:
    write_file(_db,
               _etl_claim(_db, "cache", "TRGCache", "TotalAmountPaid"),
               _etl_mining(_db))

# ── Special paid columns ──────────────────────────────────────────────────────
write_file("BCBSARRx",
           _etl_claim("BCBSARRx", "claim", "TRGClaim", "DRUGPYALLOWEDPAID"),
           _etl_mining("BCBSARRx"))

write_file("CenteneFidelisRx",
           _etl_claim("CenteneFidelisRx", "cache", "TRGCache", "payamount"),
           _etl_mining("CenteneFidelisRx"))

write_file("ElixirRx",
           _etl_claim("ElixirRx", "claim", "TRGClaim", "TOTALAMOUNTPAID"),
           _etl_mining("ElixirRx"))

write_file("EverNorthRx",
           _etl_claim("EverNorthRx", "claim", "TRGClaim", "SubrogationPaidAmount"),
           _etl_mining("EverNorthRx"))

write_file("ExcellusRx",
           _etl_claim("ExcellusRx", "claim", "TRGClaim", "cTotalAmountPaid"),
           _etl_mining("ExcellusRx"))

write_file("WellcareRx",
           _etl_claim("WellcareRx", "claim", "TRGClaim", "AmountPaid"),
           _etl_mining("WellcareRx"))

# ── ElevanceMMMRx: claim query is malformed in source — mining only ───────────
write_file("ElevanceMMMRx",
           None,
           _etl_mining("ElevanceMMMRx"))

# ── CM9: date-named claim tables — mining (dbo.RxClaims) only ────────────────
write_file("HMSA_Rx",
           None,
           _cm9_mining("HMSA_Rx"))

write_file("NYSHIP_Rx",
           None,
           _cm9_mining("NYSHIP_Rx", "PatientPayAmount"))

# ── CM9: vwClaimHistory + dbo.RxClaims (special CASE logic) ──────────────────
write_file(
    "BCBSNC_Rx",
    (
        "SELECT TapeID,\n"
        "    FORMAT(SUM(CASE WHEN [INSURANCE_PAID_SIGN] = '-'\n"
        "        THEN [INSURANCE_PAID_AMOUNT] * -1\n"
        "        ELSE [INSURANCE_PAID_AMOUNT] END), 'C', 'en-US') [Paid],\n"
        "    Format(count(*), 'N0') [Records]\n"
        "FROM [BCBSNC_Rx].[dbo].[vwClaimHistory] (nolock)\n"
        "WHERE TapeID IN ({TAPEIDS})\n"
        "AND TRG_DupeIndicator = 'N'\n"
        "GROUP BY TapeID\n"
        "ORDER BY TapeID"
    ),
    _cm9_mining("BCBSNC_Rx"),
)

write_file(
    "WellpointEdwardRx",
    (
        "SELECT [C].[TapeID],\n"
        "    FORMAT(SUM(CASE WHEN [cSplitClaimIndicator] = 'Y'\n"
        "        THEN [cSplitAmountPaid_sum]\n"
        "        ELSE [AmountPaid] END), 'C', 'en-US') [Paid],\n"
        "    Format(count(*), 'N0') [Records]\n"
        "FROM [WellpointEdwardRx].[dbo].[vwClaimHistory] [C] (nolock)\n"
        "WHERE [C].[TapeID] IN ({TAPEIDS})\n"
        "AND [C].[TRG_DupeIndicator] = 'N'\n"
        "GROUP BY [C].[TapeID]\n"
        "ORDER BY [C].[TapeID]"
    ),
    (
        "SELECT R.TAPEID AS TapeID, FORMAT(Sum(TotalAmountPaid), 'C', 'en-US') [Paid],\n"
        "    Format(count(*), 'N0') [Records]\n"
        "FROM [WellpointEdwardRx].[dbo].[RXCLAIMS] R (nolock)\n"
        "WHERE R.TAPEID IN ({TAPEIDS})\n"
        "GROUP BY R.TAPEID\n"
        "ORDER BY R.TAPEID"
    ),
)

count = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".sql")])
print(f"\nDone — {count} files written to rx_verify_queries/")
