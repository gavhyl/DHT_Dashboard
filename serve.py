"""Production WSGI entry point. Runs the Flask app under Waitress.

Configured via env vars:
  PORT         — listen port (default 5000; staging service uses 5001)
  HOST         — bind address (default 0.0.0.0)
  THREADS      — Waitress worker threads (default 8)

NSSM service runs:   py serve.py
"""
import os
import time

from waitress import serve

from app import app
import ramp


def _warm_caches():
    """Populate slow external caches before Waitress starts accepting traffic.

    Cold RAMP fetch is ~13s for the QueueCard list; without this warming the
    first user request after startup (or after the 5-min TTL expires) eats
    that cost. We can't avoid the 5-min refresh cost — but at least the very
    first request on a freshly started service is fast.
    """
    print("Warming external caches before accepting traffic...", flush=True)
    start = time.perf_counter()
    try:
        ramp.get_delivery_tickets()
    except Exception as e:
        print(f"  RAMP warm failed: {e!r}", flush=True)
    try:
        ramp.get_kaiser_delivery_tickets()
    except Exception as e:
        print(f"  Kaiser ADO warm failed: {e!r}", flush=True)
    print(f"  done in {(time.perf_counter() - start):.1f}s", flush=True)


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    threads = int(os.environ.get("THREADS", "8"))
    _warm_caches()
    serve(app, host=host, port=port, threads=threads)
