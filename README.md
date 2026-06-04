# DHT Dashboard

Internal web app the Data Delivery team uses to review **DHT claims certifications** before delivery — pending vs. certified certs, validation issues, file loads, Rx claim/mining verification, RAMP/ADO delivery tickets, and an automated **READY / REVIEW** verdict.

> Operational runbooks (deploy, onboarding, weekly review) live in Notion under **Data Operations → Data Operations Runbooks → DHT Dashboard Runbooks**.

## Stack

- **Python 3** · **Flask** (web framework)
- **Waitress** WSGI server in production (`serve.py`), managed as an **NSSM** Windows service
- **pyodbc** against SQL Server (Windows / Trusted authentication)
- Integrates with **RAMP** (NTLM) and **Azure DevOps / TFS** (PAT)

## How the pieces fit

| File | Responsibility |
|------|----------------|
| `app.py` | Flask routes: `/` (client view), `/cert/<id>` (cert detail), `/analyze` (batch verdicts) |
| `db.py` | All `DHTStats` queries + Kaiser aggregation logic |
| `ramp.py` | RAMP QueueCard fetch + ADO work-item metadata (delivery-ticket matching) |
| `file_loads.py` / `rx_verify.py` | Per-client SQL run against the ETL servers in `file_load_queries/servers.json` |
| `analysis.py` | Rule-based READY/REVIEW engine (no external/LLM calls) |
| `serve.py` | Production entry point (Waitress); warms RAMP/ADO caches before serving |
| `templates/` | Jinja templates (`index.html`, `cert.html`, `base.html`) |
| `file_load_queries/` | Per-client file-load `.sql` + `servers.json` (DatabaseName → ETL server) |
| `rx_verify_queries/` | Per-client Rx verification `.sql` (`--CLAIM--` / `--MINING--` sections) |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running

**Development:**

```bash
py app.py          # Flask dev server on http://localhost:5000 (debug)
```

**Production:** run under Waitress via `serve.py`, wrapped as an NSSM service:

```bash
py serve.py        # honors PORT / HOST / THREADS env vars
```

## Configuration (environment variables)

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | `5000` | Listen port (staging instance uses `5001`) |
| `HOST` | `0.0.0.0` | Bind address |
| `THREADS` | `8` | Waitress worker threads |
| `DHT_CONN_STR` | `TRGUTIL10 / DHTStats` (Trusted) | Primary DB connection string |
| `ADO_PAT` | *(empty)* | **ADO Personal Access Token** — required for delivery-ticket lookups |
| `RAMP_URL` | `http://ramp` | RAMP base URL |
| `ADO_BASE` | `https://devops.ado.rawlingslou.prod/TFS2012` | ADO/TFS base URL |
| `ADO_DELIVERY_AREA` | `Rawlings\RDP\Data Operations` | Area path that scopes "open" delivery tickets |
| `DHT_QUERY_DIR` | `./file_load_queries` | Folder of per-client file-load `.sql` + `servers.json` |
| `DHT_RX_VERIFY_DIR` | `./rx_verify_queries` | Folder of per-client Rx verification `.sql` |
| `DHT_PER_TYPE_CAP` | `50` | Max File Loads rows kept per file type |

No credentials are stored in the repo — SQL and RAMP use Windows/Trusted auth (the service identity), and ADO uses the `ADO_PAT` environment variable.

## Deployment

Runs on **trgdatacap2** as two NSSM Windows services under the `svc_dhtdash` service account:

- `DHTDashboard` — production, port **5000**
- `DHTDashboard-Staging` — QA / pre-prod, port **5001**

Deploy to staging first, validate, then promote the same build to production. The host needs Python 3 and the release runs `pip install -r requirements.txt`. See the Notion runbooks for the full procedure.

## Adding a client

1. Add a `DatabaseName → ETL server` entry to `file_load_queries/servers.json`.
2. Add `file_load_queries/<DatabaseName>.sql` (the app auto-injects a 14-day date filter and a per-file-type row cap).
3. For pharmacy clients, add `rx_verify_queries/<DatabaseName>.sql` with `--CLAIM--` / `--MINING--` markers and the `{TAPEIDS}` placeholder, and set the `isPharmacy` config flag.

`.sql` files and `servers.json` are read fresh on every request — no restart needed for query changes. See the **Onboard a New Client** runbook for details.
