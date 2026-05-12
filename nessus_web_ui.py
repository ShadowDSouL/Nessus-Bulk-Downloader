#!/usr/bin/env python3
"""
Nessus Bulk Downloader — Web UI Server
Run: python nessus_web_ui.py
Then open http://localhost:5000 in your browser.
"""

import os
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from nessus_downloader import NessusClient, BulkDownloader

app = Flask(__name__)

# Global state for active jobs
jobs = {}
jobs_lock = threading.Lock()


def make_job_id():
    return f"job_{int(time.time() * 1000)}"


def run_download_job(job_id: str, config: dict):
    logs = []
    def log(msg):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        logs.append(entry)
        with jobs_lock:
            if job_id in jobs:
                jobs[job_id]["logs"] = logs[:]

    with jobs_lock:
        jobs[job_id]["status"] = "running"

    try:
        log("Connecting to Nessus...")
        client = NessusClient(
            host=config["host"],
            port=int(config.get("port", 8834)),
            username=config.get("username"),
            password=config.get("password"),
            access_key=config.get("access_key"),
            secret_key=config.get("secret_key"),
            verify_ssl=config.get("verify_ssl", False)
        )
        log("✓ Connected successfully")

        output_dir = config.get("output_dir", "./nessus_downloads")
        formats = config.get("formats", ["nessus", "html", "csv"])
        workers = int(config.get("workers", 3))
        scan_ids = config.get("scan_ids") or None
        folder_id = config.get("folder_id") or None

        downloader = BulkDownloader(
            client=client,
            output_dir=output_dir,
            formats=formats,
            max_workers=workers,
            log_callback=log
        )

        results = downloader.run(scan_ids=scan_ids, folder_id=folder_id)

        report_path = Path(output_dir) / f"download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)

        log(f"\n✓ Done! Success: {len(results['success'])} | Failed: {len(results['failed'])} | Skipped: {len(results['skipped'])}")
        log(f"Report saved to: {report_path}")

        with jobs_lock:
            jobs[job_id]["status"] = "done"
            jobs[job_id]["results"] = results
            jobs[job_id]["report_path"] = str(report_path)

        try:
            client.logout()
        except:
            pass

    except Exception as e:
        log(f"✗ Error: {e}")
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/test-connection", methods=["POST"])
def test_connection():
    data = request.json
    try:
        client = NessusClient(
            host=data["host"],
            port=int(data.get("port", 8834)),
            username=data.get("username"),
            password=data.get("password"),
            access_key=data.get("access_key"),
            secret_key=data.get("secret_key"),
            verify_ssl=data.get("verify_ssl", False)
        )
        scans = client.get_scans()
        folders = client.get_folders()
        client.logout()
        return jsonify({"ok": True, "scan_count": len(scans), "folders": folders, "scans": scans})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/start-download", methods=["POST"])
def start_download():
    config = request.json
    job_id = make_job_id()

    with jobs_lock:
        jobs[job_id] = {
            "id": job_id,
            "status": "pending",
            "logs": [],
            "results": None,
            "config": config,
            "started_at": datetime.now().isoformat()
        }

    thread = threading.Thread(target=run_download_job, args=(job_id, config), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/job/<job_id>")
def get_job(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/api/jobs")
def list_jobs():
    with jobs_lock:
        return jsonify(list(jobs.values()))


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  Nessus Bulk Downloader — Web UI")
    print("  Open http://localhost:5000 in your browser")
    print("="*55 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
