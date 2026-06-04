import os
import re
import time
import warnings
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from requests_ntlm import HttpNtlmAuth
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RAMP_URL = os.environ.get("RAMP_URL", "http://ramp")
ADO_BASE = os.environ.get("ADO_BASE", "https://devops.ado.rawlingslou.prod/TFS2012")
ADO_DELIVERY_AREA = os.environ.get("ADO_DELIVERY_AREA", "Rawlings\\RDP\\Data Operations")

# Tickets in these states are no longer actionable for the Data Delivery team.
ADO_EXCLUDED_STATES = {"Closed"}

# These tags are applied at the end of the Delivery process, right before the
# ticket goes downstream for mining. Their presence means the Delivery team is
# done with the ticket regardless of its state.
ADO_EXCLUDED_TAGS = frozenset({
    "Certified",
    "Successful/On-Time",
    "Delayed - RDP",
    "Delayed - Client",
})

_AUTH = HttpNtlmAuth("", "")
CACHE_TTL = 300  # seconds

_cache = {"tickets": None, "fetched_at": 0.0}
_ado_meta_cache = {}  # TfsId -> (fetched_at, meta_dict|None) with CACHE_TTL
_kaiser_tickets_cache = {"tickets": None, "fetched_at": 0.0}


def _normalize(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def get_delivery_tickets(days=60):
    """Return recent Delivery Ticket QueueCards, cached for CACHE_TTL seconds.

    On a cold RAMP fetch, also warms the ADO metadata cache for every
    returned TfsId in one batched HTTP call. Without this warming, the
    per-cert find_ticket() loop on the index page can trigger hundreds of
    serial ADO metadata calls on the first request after the cache expires
    (verified: a 42-cert client was taking ~19s on cold load).
    """
    now = time.time()
    if _cache["tickets"] is not None and now - _cache["fetched_at"] < CACHE_TTL:
        return _cache["tickets"]

    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    payload = {
        "StartDate": start,
        "EndDate": end,
        "JobIds": None,
        "Status": ["Successful"],
        "CachedData": False,
    }

    try:
        r = requests.post(
            f"{RAMP_URL}/api/Ramp/QueueCard/NewList/",
            json=payload,
            auth=_AUTH,
            timeout=45,
        )
        r.raise_for_status()
        cards = r.json().get("Data", [])
        if cards and isinstance(cards[0], list):
            cards = [c for sub in cards for c in sub]
        tickets = [c for c in cards if c.get("TfsId")]
    except Exception:
        tickets = []

    _cache["tickets"] = tickets
    _cache["fetched_at"] = now

    _warm_ado_meta_cache([t["TfsId"] for t in tickets])
    return tickets


def _warm_ado_meta_cache(tfs_ids):
    """Batch-fetch ADO metadata (area/state/tags) for many work items in one
    HTTP call per chunk of 200, populating the per-ID cache. Best-effort —
    on failure individual `_get_ado_metadata` calls fall back to per-ID
    fetches as before."""
    if not tfs_ids:
        return
    now = time.time()
    pat = os.environ.get("ADO_PAT", "")
    fields = "System.AreaPath,System.State,System.Tags"
    try:
        for chunk_start in range(0, len(tfs_ids), 200):
            chunk = tfs_ids[chunk_start:chunk_start + 200]
            r = requests.get(
                f"{ADO_BASE}/_apis/wit/workItems",
                params={
                    "ids": ",".join(str(i) for i in chunk),
                    "fields": fields,
                    "api-version": "1.0",
                },
                auth=HTTPBasicAuth("", pat),
                timeout=20,
                verify=False,
            )
            r.raise_for_status()
            for item in r.json().get("value", []):
                tfs_id = item.get("id")
                if tfs_id is None:
                    continue
                f = item.get("fields", {})
                tags_raw = f.get("System.Tags") or ""
                _ado_meta_cache[tfs_id] = (now, {
                    "area": f.get("System.AreaPath"),
                    "state": f.get("System.State"),
                    "tags": {t.strip() for t in tags_raw.split(";") if t.strip()},
                })
    except Exception:
        pass


def _get_ado_metadata(tfs_id):
    """Return {area, state, tags} for an ADO work item. `tags` is a set of
    strings. None on error / not found. Cached for CACHE_TTL seconds because
    state and tags can change as the ticket moves through the workflow."""
    now = time.time()
    entry = _ado_meta_cache.get(tfs_id)
    if entry is not None and now - entry[0] < CACHE_TTL:
        return entry[1]

    meta = None
    try:
        pat = os.environ.get("ADO_PAT", "")
        r = requests.get(
            f"{ADO_BASE}/_apis/wit/workItems",
            params={
                "ids": str(tfs_id),
                "fields": "System.AreaPath,System.State,System.Tags",
                "api-version": "1.0",
            },
            auth=HTTPBasicAuth("", pat),
            timeout=10,
            verify=False,
        )
        r.raise_for_status()
        items = r.json().get("value", [])
        if items:
            f = items[0].get("fields", {})
            tags_raw = f.get("System.Tags") or ""
            meta = {
                "area": f.get("System.AreaPath"),
                "state": f.get("System.State"),
                "tags": {t.strip() for t in tags_raw.split(";") if t.strip()},
            }
    except Exception:
        pass
    _ado_meta_cache[tfs_id] = (now, meta)
    return meta


def get_kaiser_delivery_tickets(days=180):
    """Return all 'Kaiser - SNAP/MINE' ADO tickets in the Delivery area path
    from the last N days, cached for CACHE_TTL seconds.

    Kaiser delivery tickets aren't generated by RAMP — the client owner runs a
    SQL Agent job that creates the ADO work item directly — so the QueueCard
    path used by find_ticket() doesn't apply. This goes to ADO via WIQL.

    Each ticket: {TfsId, Title, JobName, State, Tags, AreaPath, ChangedDate,
    CreatedDate}. `JobName` is aliased to `Title` so the existing index
    template's `c.ramp_ticket.JobName` tooltip renders cleanly.
    """
    now = time.time()
    if (
        _kaiser_tickets_cache["tickets"] is not None
        and now - _kaiser_tickets_cache["fetched_at"] < CACHE_TTL
    ):
        return _kaiser_tickets_cache["tickets"]

    tickets = []
    try:
        pat = os.environ.get("ADO_PAT", "")
        wiql = {
            "query": (
                "SELECT [System.Id] FROM WorkItems "
                f"WHERE [System.AreaPath] UNDER '{ADO_DELIVERY_AREA}' "
                "AND [System.Title] = 'Kaiser - SNAP/MINE' "
                f"AND [System.ChangedDate] >= @Today - {int(days)} "
                "ORDER BY [System.ChangedDate] DESC"
            )
        }
        r = requests.post(
            f"{ADO_BASE}/_apis/wit/wiql",
            params={"api-version": "1.0"},
            json=wiql,
            auth=HTTPBasicAuth("", pat),
            timeout=20,
            verify=False,
        )
        r.raise_for_status()
        items = r.json().get("workItems", [])
        if items:
            ids_param = ",".join(str(i["id"]) for i in items)
            r2 = requests.get(
                f"{ADO_BASE}/_apis/wit/workItems",
                params={
                    "ids": ids_param,
                    "fields": (
                        "System.Title,System.AreaPath,System.State,"
                        "System.Tags,System.ChangedDate,System.CreatedDate"
                    ),
                    "api-version": "1.0",
                },
                auth=HTTPBasicAuth("", pat),
                timeout=20,
                verify=False,
            )
            r2.raise_for_status()
            for item in r2.json().get("value", []):
                f = item.get("fields", {})
                tags_raw = f.get("System.Tags") or ""
                title = f.get("System.Title")
                tickets.append({
                    "TfsId": item["id"],
                    "Title": title,
                    "JobName": title,
                    "State": f.get("System.State"),
                    "Tags": {t.strip() for t in tags_raw.split(";") if t.strip()},
                    "AreaPath": f.get("System.AreaPath"),
                    "ChangedDate": f.get("System.ChangedDate"),
                    "CreatedDate": f.get("System.CreatedDate"),
                })
            # ADO's `workItems?ids=...` endpoint returns items in ID-ASC
            # order regardless of how we ordered the WIQL — sort here so
            # tickets[0] is the most recently created ticket (used by
            # find_kaiser_delivery_ticket for the panel header).
            tickets.sort(key=lambda t: t.get("CreatedDate") or "", reverse=True)
    except Exception:
        pass

    _kaiser_tickets_cache["tickets"] = tickets
    _kaiser_tickets_cache["fetched_at"] = now
    return tickets


def find_kaiser_delivery_ticket():
    """Return the most recent Kaiser - SNAP/MINE ticket (for the panel
    header), or None. Just the first entry of get_kaiser_delivery_tickets()
    since that query is already ChangedDate-DESC ordered."""
    tickets = get_kaiser_delivery_tickets()
    return tickets[0] if tickets else None


def find_kaiser_ticket_for_cert(alert_timestamp, tickets=None):
    """Match a Kaiser - SNAP/MINE ticket to a specific cert by aligning the
    ticket's CreatedDate to the cert's delivery week (Thu→Wed). Used for
    previously certified Kaiser certs so each row surfaces the ticket that
    handled its delivery, not the current week's ticket.

    Returns None when no candidate is within 14 days of the cert's anchor
    Wednesday — better an empty cell than a clearly wrong ticket.
    """
    if tickets is None:
        tickets = get_kaiser_delivery_tickets()
    if not tickets or alert_timestamp is None:
        return None

    alert_dt = alert_timestamp
    if hasattr(alert_dt, "tzinfo") and alert_dt.tzinfo is not None:
        alert_dt = alert_dt.replace(tzinfo=None)

    # Cert's anchor Wednesday = next Wed on/after AlertTimestamp.
    # (weekday(): Mon=0..Sun=6, Wed=2.)
    days_until_wed = (2 - alert_dt.weekday()) % 7
    anchor_wed = (alert_dt + timedelta(days=days_until_wed)).date()

    def _proximity(t):
        raw = (t.get("CreatedDate") or "")[:10]
        try:
            ticket_date = datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            return float("inf")
        return abs((ticket_date - anchor_wed).days)

    best = min(tickets, key=_proximity)
    return best if _proximity(best) <= 14 else None


def find_ticket(database_name, delivery_tickets, alert_timestamp=None, *, only_open=True):
    """
    Return the delivery ticket best matching this database name and cert timestamp.

    When alert_timestamp is provided, candidates are sorted by absolute time
    proximity to it — the RAMP job runs and creates the ADO ticket just before
    the cert alert fires, so the closest card in time is the right one for that
    specific cert. Without a timestamp, falls back to most-recent.

    Only considers cards whose ADO work item area is ADO_DELIVERY_AREA.

    `only_open=True` (default) additionally skips tickets the Delivery team is
    done with — state in ADO_EXCLUDED_STATES or any tag in ADO_EXCLUDED_TAGS.
    Use only_open=False for already-certified certs, where the relevant ticket
    is the historical (now Closed / tagged-complete) ticket that was used.
    """
    db_norm = _normalize(database_name)
    matches = []

    for card in delivery_tickets:
        if not card.get("TfsId"):
            continue
        job_prefix = card["JobName"].replace("Delivery Ticket", "").strip()
        job_norm = _normalize(job_prefix)
        if job_norm.startswith(db_norm):
            matches.append(card)

    if not matches:
        return None

    if alert_timestamp is not None:
        alert_dt = alert_timestamp
        if hasattr(alert_dt, "tzinfo") and alert_dt.tzinfo is not None:
            alert_dt = alert_dt.replace(tzinfo=None)

        def _proximity(card):
            raw = (card.get("CreateDate") or "")[:19]
            try:
                create_dt = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return float("inf")
            return abs((create_dt - alert_dt).total_seconds())

        matches.sort(key=_proximity)
    else:
        matches.sort(key=lambda c: c.get("CreateDate", ""), reverse=True)

    for card in matches:
        meta = _get_ado_metadata(card["TfsId"])
        if not meta:
            continue
        if meta["area"] != ADO_DELIVERY_AREA:
            continue
        if only_open:
            # Skip tickets the Delivery team is done with — either Closed in
            # ADO, or carrying a completion tag applied at the final step
            # before the ticket goes downstream for mining. Disabled for
            # already-certified certs (whose ticket is by definition done).
            if meta["state"] in ADO_EXCLUDED_STATES:
                continue
            if meta["tags"] & ADO_EXCLUDED_TAGS:
                continue
        return card

    return None
