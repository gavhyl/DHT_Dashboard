"""
Rule-based confidence assessment for DHT certifications.
Compares current validation issues against per-field historical frequency
to distinguish new problems from known recurring exceptions.
"""
import calendar
from datetime import timedelta

import holidays

_US_HOLIDAYS = holidays.US()


def _backsweep_note(backsweep_files):
    """Annotation when the cert contains files flagged as likely backsweeps."""
    if not backsweep_files:
        return None
    n = len(backsweep_files)
    if n == 1:
        f = backsweep_files[0]
        reasons = ", ".join(f.get("Reasons") or [])
        return (
            f"Note: potential backsweep file detected — {f['FileName']} "
            f"({reasons}). Historical claims being delivered out-of-cycle."
        )
    return (
        f"Note: {n} potential backsweep files detected — see callout above the "
        f"Files tab. Historical claims being delivered out-of-cycle."
    )


def _eom_som_note(current_size, recent_sizes):
    """If the cert's mining-claim file size is well below the recent median for
    this client (≤ 60%), return an annotation flagging it as a likely EOM/SOM
    catch-up delivery. Client-agnostic — the caller scopes which clients this
    runs for. Returns None when there's not enough data or the size is in the
    normal range."""
    if current_size is None or not recent_sizes:
        return None
    if len(recent_sizes) < 5:
        return None
    sizes = sorted(recent_sizes)
    median = sizes[len(sizes) // 2]
    if median <= 0:
        return None
    if current_size >= median * 0.6:
        return None
    return (
        f"Note: claim file size ({current_size / 1e9:.1f} GB) is well below the "
        f"recent median ({median / 1e9:.1f} GB) — likely the monthly EOM/SOM "
        f"catch-up delivery."
    )


def _holiday_note(ts):
    """If the cert date is on or the day after a US federal holiday, return a
    short note for the reviewer; otherwise None."""
    if ts is None:
        return None
    d = ts.date() if hasattr(ts, "date") else ts
    name = _US_HOLIDAYS.get(d)
    if name:
        return (
            f"Note: {d.strftime('%A %Y-%m-%d')} is {name} — "
            f"delivery patterns may differ from a typical {d.strftime('%A')}."
        )
    prev = d - timedelta(days=1)
    name = _US_HOLIDAYS.get(prev)
    if name:
        return (
            f"Note: prior day ({prev.strftime('%A %Y-%m-%d')}) was {name} — "
            f"expect possible catch-up volumes."
        )
    return None


def _is_daily_client(history):
    """True if recent certified deliveries average less than 2 days apart."""
    timestamps = sorted(
        h["AlertTimestamp"] for h in history if h["AlertTimestamp"]
    )
    if len(timestamps) < 2:
        return False
    gaps = [(timestamps[i + 1] - timestamps[i]).days for i in range(len(timestamps) - 1)]
    return (sum(gaps) / len(gaps)) < 2


def _is_monthly_client(history):
    """True if recent certified deliveries average 20 or more days apart."""
    timestamps = sorted(
        h["AlertTimestamp"] for h in history if h["AlertTimestamp"]
    )
    if len(timestamps) < 2:
        return False
    gaps = [(timestamps[i + 1] - timestamps[i]).days for i in range(len(timestamps) - 1)]
    return (sum(gaps) / len(gaps)) >= 20


def _select_history_window(cert, history, month_history=None, dow_history=None):
    """
    Return (field_window, threshold_window, basis).

    field_window     — used for is_recurring / field-frequency: a field flagged
                       across either recent months or prior years' same month
                       counts as known (so chronic year-round issues don't get
                       falsely surfaced as new just because the prior-year same
                       month happened to miss them).
    threshold_window — used for the threshold-spike baseline: for monthly
                       clients this is prior-year same-month only, so a normal
                       seasonal volume doesn't look like a spike vs. a mixed
                       average diluted by quieter non-seasonal months.

    Basis is one of "dow", "month", "recent" and drives the insight wording.
    Monthly clients fall through to "recent" when no prior-year same-month
    history is available yet (e.g., newer clients).
    """
    if _is_daily_client(history):
        if dow_history:
            return dow_history, dow_history, "dow"
        ref = cert.get("AlertTimestamp")
        if ref is None:
            return history[:7], history[:7], "recent"
        if hasattr(ref, "tzinfo") and ref.tzinfo is not None:
            ref = ref.replace(tzinfo=None)
        cutoff = ref - timedelta(days=7)
        window = [
            h for h in history
            if h["AlertTimestamp"] and h["AlertTimestamp"].replace(tzinfo=None) >= cutoff
        ]
        return window, window, "recent"

    if month_history and _is_monthly_client(history):
        recent = history[:5]
        seen = {h["CertID"] for h in recent}
        combined = recent + [h for h in month_history if h["CertID"] not in seen]
        return combined, month_history, "month"

    recent = history[:5]
    return recent, recent, "recent"


def generate(cert, issues, history, rx_tapes, rx_has_claim, month_history=None, dow_history=None,
             claim_file_size=None, recent_claim_file_sizes=None, backsweep_files=None,
             kaiser_keys=None):
    """
    Return (verdict, insights, error).
    verdict:  "READY" or "REVIEW"
    insights: up to 3 sentences explaining the key factors
    error:    always None (no external calls)

    kaiser_keys: when provided ({'TrustScoreZ': ..., 'DuplicateLineKey': ...}),
    apply the Kaiser delivery override — if both values are ≤ 1, the cert is
    considered good to deliver regardless of other validation issues (those
    feeds chronically show field-level flags but deliver weekly based on
    these two metrics).
    """
    field_window, threshold_window, basis = _select_history_window(
        cert, history, month_history, dow_history
    )
    n_hist = len(field_window)
    current_thresh = cert.get("ThresholdCount") or 0
    non_normal = [i for i in issues if i["Determination"] != 0]

    ts = cert.get("AlertTimestamp")
    if basis == "month" and ts:
        label_long = f"recent and prior {calendar.month_name[ts.month]} deliveries"
        label_short = f"prior {calendar.month_name[ts.month]}"
    elif basis == "dow" and ts:
        label_long = f"recent {calendar.day_name[ts.weekday()]} deliveries"
        label_short = f"recent {calendar.day_name[ts.weekday()]}"
    else:
        label_long = "recent delivery history"
        label_short = "recent"

    # Build per-field frequency map across the field-frequency window
    # (combined recent + prior-year same-month for monthly clients).
    # A field is "recurring" if flagged in more than half of those certs.
    field_freq = {}
    for h in field_window:
        for issue in h.get("Issues", []):
            name = issue["FieldName"]
            field_freq[name] = field_freq.get(name, 0) + 1

    def is_recurring(field_name):
        return n_hist > 0 and field_freq.get(field_name, 0) > n_hist / 2

    # Classify current issues
    new_severe   = [i for i in non_normal if i["Determination"] == -2 and not is_recurring(i["FieldName"])]
    new_high     = [i for i in non_normal if i["Determination"] == -1 and not is_recurring(i["FieldName"])]
    known_issues = [i for i in non_normal if is_recurring(i["FieldName"])]

    # Rx mismatches (only meaningful when claim data is present)
    rx_mismatches = []
    if rx_has_claim:
        rx_mismatches = [
            t for t in (rx_tapes or [])
            if not t["match"] and t["claim_paid"] and t["mining_paid"]
        ]

    # Threshold spike vs seasonal baseline (prior-year same-month for monthly
    # clients, same-weekday for daily, recent otherwise). Using the seasonal
    # baseline avoids false spikes when a normal April happens to be quieter
    # or busier than non-April months.
    threshold_spike = False
    avg_thresh = 0.0
    if threshold_window and current_thresh > 0:
        n_thresh = len(threshold_window)
        avg_thresh = sum(h["ThresholdCount"] or 0 for h in threshold_window) / n_thresh
        if current_thresh > max(avg_thresh * 2, avg_thresh + 3):
            threshold_spike = True

    # ── Verdict ──────────────────────────────────────────────────────────────
    verdict = "REVIEW" if (new_severe or rx_mismatches or threshold_spike or len(new_high) > 2) else "READY"

    # Kaiser override — TrustScore z-score and Duplicate Line Key are the
    # team's actual delivery gate for Kaiser feeds. When both are at or near
    # zero (≤ 1), the cert is good to deliver weekly even if other validation
    # fields are flagged. Only flip a REVIEW to READY; if the verdict is
    # already READY, the override is a no-op and we don't bother surfacing it.
    kaiser_override_active = False
    if kaiser_keys and verdict == "REVIEW":
        tsz = kaiser_keys.get("TrustScoreZ")
        dup = kaiser_keys.get("DuplicateLineKey")
        if (tsz is not None and tsz <= 1 and
                dup is not None and dup <= 1):
            verdict = "READY"
            kaiser_override_active = True

    # ── Insights (max 3 sentences) ────────────────────────────────────────────
    parts = []

    # Sentence 1 — validation issue summary
    if not non_normal and current_thresh == 0:
        parts.append("No threshold hits or validation issues detected.")
    elif new_severe:
        names = ", ".join(i["FieldName"] for i in new_severe[:3])
        extra = f" and {len(new_severe) - 3} more" if len(new_severe) > 3 else ""
        parts.append(
            f"{len(new_severe)} new severe risk issue(s) not seen in {label_long}: {names}{extra}."
        )
    elif known_issues and not new_high:
        parts.append(
            f"{len(known_issues)} validation issue(s) present, all consistent with "
            f"{label_long} for this client."
        )
    elif known_issues and new_high:
        names = ", ".join(i["FieldName"] for i in new_high[:3])
        extra = f" and {len(new_high) - 3} more" if len(new_high) > 3 else ""
        parts.append(
            f"{len(known_issues)} recurring exception(s) consistent with {label_long}; "
            f"{len(new_high)} new high risk issue(s) flagged: {names}{extra}."
        )
    elif new_high:
        names = ", ".join(i["FieldName"] for i in new_high[:3])
        extra = f" and {len(new_high) - 3} more" if len(new_high) > 3 else ""
        parts.append(
            f"{len(new_high)} new high risk issue(s) not seen in {label_long}: {names}{extra}."
        )

    # Sentence 2 — Rx verification
    if rx_mismatches:
        tapes = ", ".join(str(t["TapeID"]) for t in rx_mismatches)
        parts.append(
            f"Rx claim/mining mismatch on tape(s) {tapes} — verify totals before delivery."
        )
    elif rx_tapes and rx_has_claim and verdict == "REVIEW":
        if all(t["match"] for t in rx_tapes):
            parts.append("Rx claim and mining totals match across all tapes.")

    # Sentence 3 — threshold trend (only if not already at 3 sentences)
    if threshold_spike and len(parts) < 3:
        parts.append(
            f"Threshold hits ({current_thresh}) are significantly above the "
            f"{label_short} average ({avg_thresh:.1f})."
        )

    # Context notes — prepended so the reviewer reads them first. Cap lifts
    # by one per note so threshold or Rx content isn't displaced just because
    # we added annotations.
    context_notes = []
    note = _holiday_note(ts)
    if note:
        context_notes.append(note)
    note = _eom_som_note(claim_file_size, recent_claim_file_sizes)
    if note:
        context_notes.append(note)
    note = _backsweep_note(backsweep_files)
    if note:
        context_notes.append(note)

    parts = context_notes + parts
    max_parts = 3 + len(context_notes)

    # Lead with the Kaiser override note when it changed the verdict so the
    # reviewer immediately sees why issues didn't flip this to REVIEW. The
    # cap bumps by one so the override doesn't crowd out the issue summary.
    if kaiser_override_active:
        tsz = kaiser_keys["TrustScoreZ"]
        dup = kaiser_keys["DuplicateLineKey"]
        parts.insert(
            0,
            f"Kaiser delivery criteria met — Trust Score z={tsz:.2f}, "
            f"Duplicate Line Key={dup:.0f} (both <= 1)."
        )
        max_parts += 1

    insights = " ".join(parts[:max_parts]) or "No significant concerns identified."
    return verdict, insights, None
