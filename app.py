from concurrent.futures import ThreadPoolExecutor

from flask import Flask, render_template, abort, request, redirect, url_for, jsonify
import db
import ramp
import file_loads
import rx_verify
import analysis

# Cap the analyze-batch worker pool. Each worker runs the full per-cert
# pipeline (10+ DB round trips). 8 strikes a balance between batch latency
# and not overwhelming SQL Server / pyodbc's connection pool.
_ANALYZE_BATCH_WORKERS = 8

app = Flask(__name__)


@app.route("/")
def index():
    clients = db.get_active_client_names()
    selected = request.args.get("client", "")
    pending_certs = []
    certified_certs = []
    kaiser_matrix = None
    kaiser_ticket = None
    kaiser_coverage = None
    is_kaiser = selected == db.KAISER_AGGREGATE_NAME

    if selected:
        certs = db.get_active_certs(selected)
        cert_ids = [c["CertID"] for c in certs]
        pcns_by_cert = db.get_cert_pcns(cert_ids)
        claim_names_by_cert = db.get_cert_claim_names(cert_ids)
        delivery_tickets = [] if is_kaiser else ramp.get_delivery_tickets()
        kaiser_tickets = ramp.get_kaiser_delivery_tickets() if is_kaiser else []
        for cert in certs:
            if is_kaiser:
                # Pending Kaiser certs share the current ticket shown in the
                # panel header (no per-row badge). Previously certified rows
                # surface their historical ticket — each cert belongs to a
                # different delivery week and used a different ADO ticket.
                if cert["CurrentStatus"] == "Certified":
                    cert["ramp_ticket"] = ramp.find_kaiser_ticket_for_cert(
                        cert.get("AlertTimestamp"), kaiser_tickets
                    )
                else:
                    cert["ramp_ticket"] = None
            else:
                cert["ramp_ticket"] = ramp.find_ticket(
                    selected, delivery_tickets, cert.get("AlertTimestamp"),
                    only_open=cert["CurrentStatus"] != "Certified",
                )
            cert["pcns"] = pcns_by_cert.get(cert["CertID"], [])
            cert["claim_names"] = claim_names_by_cert.get(cert["CertID"], [])
        pending_certs = [c for c in certs if c["CurrentStatus"] == "Email sent, Ready for Certification review"]
        certified_certs = [c for c in certs if c["CurrentStatus"] == "Certified"]

        if is_kaiser:
            kaiser_matrix = db.get_kaiser_weekly_matrix()
            kaiser_ticket = kaiser_tickets[0] if kaiser_tickets else None
            kaiser_coverage = db.get_kaiser_paid_date_coverage()

    return render_template(
        "index.html", clients=clients, selected=selected,
        pending_certs=pending_certs, certified_certs=certified_certs,
        kaiser_matrix=kaiser_matrix, kaiser_ticket=kaiser_ticket,
        kaiser_coverage=kaiser_coverage,
    )


@app.route("/cert/<int:cert_id>")
def cert_detail(cert_id):
    cert = db.get_cert(cert_id)
    if not cert:
        abort(404)

    tables = db.get_cert_tables(cert_id)
    issues = db.get_cert_issues(cert_id)
    comments = db.get_comments(cert["DatabaseName"])
    delivery_tickets = ramp.get_delivery_tickets()
    ramp_ticket = ramp.find_ticket(
        cert["DatabaseName"], delivery_tickets, cert.get("AlertTimestamp"),
        only_open=cert["CurrentStatus"] != "Certified",
    )
    fl_cols, fl_rows, fl_error = file_loads.get_file_loads(
        cert["DatabaseName"], alert_timestamp=cert.get("AlertTimestamp")
    )

    rx_tapes, rx_has_claim, rx_error = None, False, None
    if cert["isPharmacy"] == "1":
        tape_ids = db.get_cert_claim_tapeids(cert_id)
        claim_rows, mining_rows, rx_error = rx_verify.get_rx_verification(
            cert["DatabaseName"], tape_ids
        )
        if claim_rows is not None or mining_rows is not None:
            rx_tapes = rx_verify.merge_by_tape(claim_rows, mining_rows)
            rx_has_claim = bool(claim_rows)

    backsweep_files = db.get_cert_backsweep_files(cert_id)

    # Kaiser feeds collapse to a single dropdown entry, so the back link
    # should return to the aggregated Kaiser view rather than the per-feed
    # standalone page (e.g. /?client=Kaiser_CO would render an unaggregated
    # view that the dropdown no longer surfaces).
    if cert["DatabaseName"] in db.KAISER_AGGREGATE_DATABASES:
        back_client = db.KAISER_AGGREGATE_NAME
    else:
        back_client = cert["DatabaseName"]

    return render_template(
        "cert.html",
        cert=cert,
        tables=tables,
        issues=issues,
        comments=comments,
        ramp_ticket=ramp_ticket,
        fl_cols=fl_cols,
        fl_rows=fl_rows,
        fl_error=fl_error,
        rx_tapes=rx_tapes,
        rx_has_claim=rx_has_claim,
        rx_error=rx_error,
        backsweep_files=backsweep_files,
        back_client=back_client,
    )


@app.route("/cert/<int:cert_id>/comment", methods=["POST"])
def add_comment(cert_id):
    cert = db.get_cert(cert_id)
    if not cert:
        abort(404)

    comment_text = request.form.get("comment", "").strip()
    if not comment_text:
        return redirect(url_for("cert_detail", cert_id=cert_id, error="comment_required"))

    db.add_comment(
        database_name=cert["DatabaseName"],
        pcn=request.form.get("pcn"),
        tape_id=request.form.get("tape_id"),
        category=request.form.get("category"),
        tfs=request.form.get("tfs"),
        comment=comment_text,
    )
    return redirect(url_for("cert_detail", cert_id=cert_id, added=1))


def _analyze_cert_by_id(cert_id):
    """Run the full analysis pipeline for one cert. Returns a result dict
    with cert_id, alert (ISO), database, verdict, insights, error. `error` is
    None on success; verdict/insights are None on error. Shared by the
    single-cert and weekly-batch endpoints."""
    cert = db.get_cert(cert_id)
    if not cert:
        return {"cert_id": cert_id, "error": "cert not found"}

    issues = db.get_cert_issues(cert_id)
    history = db.get_recent_cert_history(cert["DatabaseName"], cert_id)

    month_history = None
    dow_history = None
    alert_ts = cert.get("AlertTimestamp")
    if alert_ts:
        month_history = db.get_same_month_cert_history(
            cert["DatabaseName"], cert_id, alert_ts.month, alert_ts.year
        )
        dow_history = db.get_recent_dow_cert_history(
            cert["DatabaseName"], cert_id, alert_ts.weekday()
        )

    rx_tapes, rx_has_claim = None, False
    if cert["isPharmacy"] == "1":
        tape_ids = db.get_cert_claim_tapeids(cert_id)
        claim_rows, mining_rows, _ = rx_verify.get_rx_verification(
            cert["DatabaseName"], tape_ids
        )
        if claim_rows is not None or mining_rows is not None:
            rx_tapes = rx_verify.merge_by_tape(claim_rows, mining_rows)
            rx_has_claim = bool(claim_rows)

    claim_file_size = None
    recent_claim_file_sizes = None
    if cert["DatabaseName"] == "CignaRx":
        claim_file_size = db.get_cert_claim_file_size(cert_id)
        recent_claim_file_sizes = db.get_recent_claim_file_sizes(
            cert["DatabaseName"], cert_id
        )

    backsweep_files = db.get_cert_backsweep_files(cert_id)

    kaiser_keys = None
    if cert["DatabaseName"] in db.KAISER_AGGREGATE_DATABASES:
        kaiser_keys = db.get_cert_kaiser_keys(cert_id)

    verdict, insights, error = analysis.generate(
        cert, issues, history, rx_tapes, rx_has_claim,
        month_history=month_history, dow_history=dow_history,
        claim_file_size=claim_file_size,
        recent_claim_file_sizes=recent_claim_file_sizes,
        backsweep_files=backsweep_files,
        kaiser_keys=kaiser_keys,
    )
    return {
        "cert_id": cert_id,
        "alert": alert_ts.isoformat() if alert_ts else None,
        "database": cert["DatabaseName"],
        "verdict": verdict if not error else None,
        "insights": insights if not error else None,
        "error": error,
    }


@app.route("/cert/<int:cert_id>/analysis", methods=["POST"])
def cert_analysis(cert_id):
    result = _analyze_cert_by_id(cert_id)
    if result.get("error") == "cert not found":
        abort(404)
    if result.get("error"):
        return jsonify({"error": result["error"]})
    return jsonify({"verdict": result["verdict"], "insights": result["insights"]})


@app.route("/analyze", methods=["POST"])
def analyze_multi():
    """Batch analysis for the weekly-review use case. Accepts JSON
    `{cert_ids: [int, ...]}` and returns per-cert results plus a summary."""
    payload = request.get_json(silent=True) or {}
    cert_ids = payload.get("cert_ids") or []
    if not cert_ids:
        return jsonify({"error": "no cert_ids provided"}), 400

    # Run cert analyses concurrently — each _analyze_cert_by_id makes ~10
    # independent DB queries via pyodbc, which uses its own connection pool
    # under the hood, so thread parallelism is safe and a big win here
    # (sequential ~8s/cert × 24 ≈ 3min; parallel ≈ 20-30s).
    with ThreadPoolExecutor(max_workers=_ANALYZE_BATCH_WORKERS) as pool:
        results = list(pool.map(_analyze_cert_by_id, (int(cid) for cid in cert_ids)))
    ready = sum(1 for r in results if r.get("verdict") == "READY")
    review = sum(1 for r in results if r.get("verdict") == "REVIEW")
    errors = sum(1 for r in results if r.get("error"))
    return jsonify({
        "certs": results,
        "summary": {
            "total": len(results),
            "ready": ready,
            "review": review,
            "errors": errors,
        },
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
