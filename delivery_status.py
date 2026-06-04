"""
Delivery-status calendar integration.

Wraps the vendored Client Delivery Status tool (``rdp_client_delivery_status.py``,
authored by Timothy Stroud — https://github.com/TimothyStroud/Client-Delivery-Status)
and exposes its HTML dashboard for embedding (via iframe) in the DHT Dashboard
home page.

Design (see project memory 'project-dht-delivery-status-integration'):
  * The vendored module is kept UNMODIFIED so future upstream updates are a
    drop-in file replacement. We import it and reproduce the data-gathering
    path of its ``main()`` — minus the Excel workbook and the file-copy side
    effects (network share / OneDrive / local archive), which don't belong in
    a web app. ``build_dashboard_html()`` is reused as-is for the markup.
  * The full 12-month calendar is expensive to build (many sqlcmd/curl round
    trips), so the rendered HTML is cached for the day and rebuilt on date
    rollover. ``serve.py`` warms this at startup like the RAMP/ADO caches.
"""
import calendar as _cal
import os
import threading
from datetime import date, timedelta

import rdp_client_delivery_status as cds

# Cache the rendered HTML for the calendar day it was built for. The build is
# expensive and the calendar only changes day-to-day, so one build per day
# (plus the startup warm) is plenty. A lock serializes concurrent cold builds
# under Waitress's worker threads so we never run the fetch storm twice at once.
_LOCK = threading.Lock()
_CACHE = {"html": None, "built_for": None}  # built_for: date the cache reflects

# Dark-mode override, appended after the vendored stylesheet so the embedded
# calendar matches the rest of the (Bootstrap dark) dashboard. We only re-theme
# the neutral surfaces + the few selectors that hardcode light values or reuse
# --accent-dark as a *text* color (unreadable on a dark surface). The semantic
# highlight fills (alert/yellow/holiday/today) are intentionally left bright so
# they still pop against the dark grid. Because this is variable-based and
# appended, it survives upstream CSS edits as long as the var/class names hold.
_DARK_THEME_CSS = """
:root {
  --bg: #212529; --card: #2b3035; --border: #495057;
  --text: #dee2e6; --muted: #adb5bd; --day-fill: #323a42;
}
body { background: var(--bg); color: var(--text); }
header.bar { background: #1a2733; }
nav.tabs { background: var(--card); border-bottom-color: var(--border); }
nav.tabs button.tab { color: #9ec5e8; }
nav.tabs button.tab.active { color: #fff; }
header.bar input[type=search] { background: #11161b; color: var(--text); }
header.bar input[type=search]::placeholder { color: var(--muted); }
.week-label { color: #9ec5e8; }
.strip td { color: var(--text); }
.strip td.dim-month, td.dim-month { background: #1a1d20 !important; color: #6c757d; }
.sec-gap td { background: var(--bg); }
.key { color: var(--muted); }
body.search-active td.client-cell.match-cell { background: #3a3320; color: #ffe28a; }
"""


def _apply_dark_theme(html):
    """Inject the dark-mode override just before </head> so it wins over the
    vendored stylesheet. No-op if the marker isn't present (defensive against
    upstream markup changes)."""
    marker = "</head>"
    if marker not in html:
        return html
    return html.replace(marker, f"<style>{_DARK_THEME_CSS}</style>{marker}", 1)


def _gather_month_packs():
    """Reproduce ``rdp_client_delivery_status.main()``'s data path, returning
    ``(month_packs, today, current_tab_name)`` WITHOUT writing the Excel
    workbook or copying files anywhere. This intentionally mirrors ``main()``
    so that upstream logic changes flow through simply by re-vendoring the
    module — only the output side is reimplemented here.
    """
    today = date.today()
    year, month = today.year, today.month
    month_start = date(year, month, 1)

    # 90 days back gives monthly clients enough history for the avg-day calc.
    certs = cds.fetch_dht_certs(since=date(year, month, 1) - timedelta(days=90))
    cert_idx = cds.build_cert_index(certs)

    tickets = cds.fetch_ado_tickets(min_changed_date=month_start - timedelta(days=14))

    jobs = cds.fetch_ramp_jobs()

    # Auto-discover new MasterLoad 0110 implementations (mirrors main()): new
    # clients default to Weekly/Monday; PBMRx → snap-kind-only, others →
    # implementation-load-only. Mutates the vendored module's config dicts.
    for entry in cds.find_unconfigured_masterload_clients(jobs):
        client = entry["raw"]
        if client not in cds.WEEKLY_CLIENTS:
            cds.WEEKLY_CLIENTS[client] = ["Monday"]
        if entry["pbmrx"]:
            cds.SNAP_KIND_ONLY_CLIENTS.add(client)
        else:
            cds.IMPLEMENTATION_LOAD_ONLY_CLIENTS.add(client)
        aliases = cds.CLIENT_ALIASES.setdefault(client, [])
        if entry["normalized"] not in aliases:
            aliases.append(entry["normalized"])

    # Auto-Inactive clients whose primary 0100/0110 jobs are all disabled.
    auto_inactive = cds.auto_inactive_from_ramp(jobs)
    if auto_inactive:
        cds.FORCED_INACTIVE.update(auto_inactive)

    queue = cds.fetch_ramp_queue()
    snaps = cds.fetch_ramp_snaps()

    since_dt = date(year, month, 1) - timedelta(days=14)
    tape_loads = {}
    for _client, (db, src_key) in cds.TAPE_LOAD_SOURCES.items():
        tape_loads[src_key] = cds.fetch_tape_loads(db, since_dt)

    multi_week_loads = {}
    for client, (db, _pattern) in cds.MULTI_WEEK_CLIENTS.items():
        multi_week_loads[client] = cds.fetch_tape_loads(db, since_dt)

    snap_idx = cds.build_snap_index(jobs, queue, snaps, tape_loads=tape_loads)

    aetna_nmsp_loads = cds.fetch_aetna_nmsp_loads(
        since=date(year, month, 1) - timedelta(days=30)
    )

    latest_tickets, monthly_placements = cds.build_ticket_index(tickets, jobs)

    current_tab_name = f"{_cal.month_name[month]} {year}"
    holidays = cds.us_federal_holidays(year)

    month_packs = []
    for m in range(1, 13):
        sec_m = wk_m = None
        # Closed 2026 months use the manually-maintained snapshot xlsx on the
        # \\trgfile1 share as source of truth. Make that read resilient: if the
        # share is unreachable (or parse fails) we fall back to the live build
        # rather than letting the whole page error out.
        snapshot_file = cds.EXPECTED_DATES_FILES.get(m) if year == 2026 else None
        if snapshot_file:
            try:
                snap_path = os.path.join(cds.EXPECTED_DATES_DIR, snapshot_file)
                if os.path.exists(snap_path):
                    sec_m, wk_m = cds.parse_all_clients_xlsx(snap_path, year)
                    if sec_m is None or not wk_m:
                        sec_m = wk_m = None
            except Exception:
                sec_m = wk_m = None

        if sec_m is None or wk_m is None:
            sec_m, wk_m = cds.plan_calendar(
                year, m, cert_idx, snap_idx, latest_tickets, monthly_placements,
                jobs, queue,
                esipbmrx_tape=tape_loads.get("esipbmrx"),
                multi_week_loads=multi_week_loads,
                aetna_nmsp_loads=aetna_nmsp_loads,
            )

        month_packs.append({
            "name": f"{_cal.month_name[m]} {year}", "year": year, "month": m,
            "sections": sec_m, "weeks": wk_m, "holidays": holidays,
        })

    return month_packs, today, current_tab_name


def _build_html():
    month_packs, today, current_tab_name = _gather_month_packs()
    html = cds.build_dashboard_html(month_packs, today, current_tab_name)
    return _apply_dark_theme(html)


def get_calendar_html(force=False):
    """Return the rendered delivery-status dashboard HTML, cached for the day.

    Rebuilds when the calendar date rolls over or when ``force=True``.
    Thread-safe; concurrent cold callers serialize on ``_LOCK`` and share the
    single build.
    """
    today = date.today()
    with _LOCK:
        if (not force and _CACHE["html"] is not None
                and _CACHE["built_for"] == today):
            return _CACHE["html"]
        html = _build_html()
        _CACHE["html"] = html
        _CACHE["built_for"] = today
        return html
