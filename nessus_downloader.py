#!/usr/bin/env python3
"""
Nessus Bulk Downloader
Automates downloading scan results from Tenable Nessus in .xlsx, .html, and .nessus formats.
"""

import os
import sys
import time
import json
import requests
import argparse
import urllib3
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NessusClient:
    def __init__(self, host: str, port: int, username: str = None, password: str = None,
                 access_key: str = None, secret_key: str = None, verify_ssl: bool = False):
        self.base_url = f"https://{host}:{port}"
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.token = None

        if access_key and secret_key:
            self.session.headers.update({
                "X-ApiKeys": f"accessKey={access_key}; secretKey={secret_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
            self.auth_method = "api_keys"
        elif username and password:
            self.username = username
            self.password = password
            self.auth_method = "password"
            self._login()
        else:
            raise ValueError("Either API keys or username/password required")

    def _login(self):
        resp = self.session.post(
            f"{self.base_url}/session",
            json={"username": self.username, "password": self.password}
        )
        resp.raise_for_status()
        self.token = resp.json()["token"]
        self.session.headers.update({
            "X-Cookie": f"token={self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def logout(self):
        if self.auth_method == "password" and self.token:
            self.session.delete(f"{self.base_url}/session")

    def get_scans(self, folder_id: Optional[int] = None) -> list:
        params = {}
        if folder_id:
            params["folder_id"] = folder_id
        resp = self.session.get(f"{self.base_url}/scans", params=params)
        resp.raise_for_status()
        return resp.json().get("scans", []) or []

    def get_folders(self) -> list:
        resp = self.session.get(f"{self.base_url}/folders")
        resp.raise_for_status()
        return resp.json().get("folders", []) or []

    def get_scan_details(self, scan_id: int) -> dict:
        resp = self.session.get(f"{self.base_url}/scans/{scan_id}")
        resp.raise_for_status()
        return resp.json()

    def export_scan(self, scan_id: int, format: str, chapters: str = None) -> str:
        payload = {"format": format}
        if format == "html" and chapters:
            payload["chapters"] = chapters
        elif format == "csv":
            payload["reportContents"] = {
                "csvColumns": {
                    "id": True, "cve": True, "cvss": True, "risk": True,
                    "hostname": True, "protocol": True, "port": True,
                    "plugin_name": True, "synopsis": True, "description": True,
                    "solution": True, "see_also": True, "plugin_output": True
                }
            }

        resp = self.session.post(
            f"{self.base_url}/scans/{scan_id}/export",
            json=payload
        )
        resp.raise_for_status()
        return resp.json()["file"]

    def check_export_status(self, scan_id: int, file_id: str) -> str:
        resp = self.session.get(
            f"{self.base_url}/scans/{scan_id}/export/{file_id}/status"
        )
        resp.raise_for_status()
        return resp.json()["status"]

    def download_export(self, scan_id: int, file_id: str) -> bytes:
        resp = self.session.get(
            f"{self.base_url}/scans/{scan_id}/export/{file_id}/download",
            stream=True
        )
        resp.raise_for_status()
        return resp.content

    def wait_for_export(self, scan_id: int, file_id: str, timeout: int = 300) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            status = self.check_export_status(scan_id, file_id)
            if status == "ready":
                return True
            elif status == "error":
                return False
            time.sleep(2)
        return False


class BulkDownloader:
    def __init__(self, client: NessusClient, output_dir: str, formats: list,
                 max_workers: int = 3, log_callback=None):
        self.client = client
        self.output_dir = Path(output_dir)
        self.formats = formats
        self.max_workers = max_workers
        self.log = log_callback or print
        self.results = {"success": [], "failed": [], "skipped": []}

    def sanitize_name(self, name: str) -> str:
        invalid = '<>:"/\\|?*'
        for ch in invalid:
            name = name.replace(ch, "_")
        return name.strip()[:100]

    def download_scan(self, scan: dict) -> dict:
        scan_id = scan["id"]
        scan_name = self.sanitize_name(scan.get("name", f"scan_{scan_id}"))

        result = {"scan_id": scan_id, "scan_name": scan_name, "formats": {}}

        for fmt in self.formats:
            try:
                self.log(f"[{scan_name}] Requesting {fmt.upper()} export...")

                chapters = "vuln_hosts_summary;vuln_by_host;compliance_exec;remediations;compliance" if fmt == "html" else None
                file_id = self.client.export_scan(scan_id, fmt, chapters)

                self.log(f"[{scan_name}] Waiting for {fmt.upper()} export (file: {file_id})...")
                ready = self.client.wait_for_export(scan_id, file_id)

                if not ready:
                    result["formats"][fmt] = "timeout"
                    self.log(f"[{scan_name}] {fmt.upper()} export timed out or errored")
                    continue

                self.log(f"[{scan_name}] Downloading {fmt.upper()}...")
                content = self.client.download_export(scan_id, file_id)

                ext_map = {"nessus": ".nessus", "html": ".html", "csv": ".csv",
                           "pdf": ".pdf", "db": ".db"}
                ext = ext_map.get(fmt, f".{fmt}")
                filepath = self.output_dir / f"{scan_name}{ext}"
                filepath.write_bytes(content)

                size_kb = len(content) / 1024
                result["formats"][fmt] = {"status": "ok", "path": str(filepath), "size_kb": round(size_kb, 1)}
                self.log(f"[{scan_name}] ✓ {fmt.upper()} saved ({size_kb:.1f} KB) → {filepath}")

            except Exception as e:
                result["formats"][fmt] = {"status": "error", "error": str(e)}
                self.log(f"[{scan_name}] ✗ {fmt.upper()} failed: {e}")

        return result

    def run(self, scan_ids: list = None, folder_id: int = None) -> dict:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.log("Fetching scan list from Nessus...")
        all_scans = self.client.get_scans(folder_id)

        if not all_scans:
            self.log("No scans found.")
            return self.results

        if scan_ids:
            scans = [s for s in all_scans if s["id"] in scan_ids]
        else:
            scans = all_scans

        completed_statuses = {"completed", "imported"}
        downloadable = [s for s in scans if s.get("status", "").lower() in completed_statuses]
        skipped = [s for s in scans if s.get("status", "").lower() not in completed_statuses]

        for s in skipped:
            self.log(f"Skipping [{s['name']}] — status: {s.get('status', 'unknown')}")
            self.results["skipped"].append(s)

        self.log(f"\n→ {len(downloadable)} scans to download | {len(skipped)} skipped | workers: {self.max_workers}\n")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.download_scan, scan): scan for scan in downloadable}
            for future in as_completed(futures):
                scan = futures[future]
                try:
                    result = future.result()
                    all_ok = all(
                        isinstance(v, dict) and v.get("status") == "ok"
                        for v in result["formats"].values()
                    )
                    if all_ok:
                        self.results["success"].append(result)
                    else:
                        self.results["failed"].append(result)
                except Exception as e:
                    self.log(f"Unexpected error for scan {scan['name']}: {e}")
                    self.results["failed"].append({"scan_name": scan["name"], "error": str(e)})

        return self.results


def main():
    parser = argparse.ArgumentParser(
        description="Nessus Bulk Downloader — Download scan results in bulk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all scans using API keys
  python nessus_downloader.py --host 192.168.1.100 --access-key KEY --secret-key SECRET

  # Download specific scans using username/password
  python nessus_downloader.py --host 192.168.1.100 -u admin -p password --scan-ids 1 2 3

  # Download only nessus and html formats
  python nessus_downloader.py --host 192.168.1.100 --access-key KEY --secret-key SECRET --formats nessus html

  # Download from a specific folder with 5 parallel workers
  python nessus_downloader.py --host 192.168.1.100 --access-key KEY --secret-key SECRET --folder-id 3 --workers 5
        """
    )

    conn_group = parser.add_argument_group("Connection")
    conn_group.add_argument("--host", required=True, help="Nessus host/IP")
    conn_group.add_argument("--port", type=int, default=8834, help="Nessus port (default: 8834)")
    conn_group.add_argument("--verify-ssl", action="store_true", help="Verify SSL certificate")

    auth_group = parser.add_argument_group("Authentication (choose one)")
    auth_group.add_argument("--access-key", help="Nessus API access key")
    auth_group.add_argument("--secret-key", help="Nessus API secret key")
    auth_group.add_argument("-u", "--username", help="Nessus username")
    auth_group.add_argument("-p", "--password", help="Nessus password")

    dl_group = parser.add_argument_group("Download Options")
    dl_group.add_argument("--formats", nargs="+",
                          choices=["nessus", "html", "csv", "pdf", "db"],
                          default=["nessus", "html", "csv"],
                          help="Formats to download (default: nessus html csv)")
    dl_group.add_argument("--scan-ids", nargs="+", type=int,
                          help="Specific scan IDs to download (default: all)")
    dl_group.add_argument("--folder-id", type=int, help="Download scans from specific folder only")
    dl_group.add_argument("--output-dir", default="./nessus_downloads",
                          help="Output directory (default: ./nessus_downloads)")
    dl_group.add_argument("--workers", type=int, default=3,
                          help="Parallel download workers (default: 3)")

    args = parser.parse_args()

    if not ((args.access_key and args.secret_key) or (args.username and args.password)):
        parser.error("Provide either --access-key + --secret-key OR --username + --password")

    print(f"\n{'='*60}")
    print(f"  Nessus Bulk Downloader")
    print(f"  Target: {args.host}:{args.port}")
    print(f"  Formats: {', '.join(args.formats)}")
    print(f"  Output: {args.output_dir}")
    print(f"{'='*60}\n")

    try:
        print("Connecting to Nessus...")
        client = NessusClient(
            host=args.host, port=args.port,
            username=args.username, password=args.password,
            access_key=args.access_key, secret_key=args.secret_key,
            verify_ssl=args.verify_ssl
        )
        print("✓ Connected successfully\n")

        downloader = BulkDownloader(
            client=client,
            output_dir=args.output_dir,
            formats=args.formats,
            max_workers=args.workers
        )

        results = downloader.run(scan_ids=args.scan_ids, folder_id=args.folder_id)

        report_path = Path(args.output_dir) / f"download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n{'='*60}")
        print(f"  Download Summary")
        print(f"{'='*60}")
        print(f"  ✓ Success : {len(results['success'])} scans")
        print(f"  ✗ Failed  : {len(results['failed'])} scans")
        print(f"  ⊘ Skipped : {len(results['skipped'])} scans")
        print(f"  Report    : {report_path}")
        print(f"{'='*60}\n")

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n[!] Cannot connect to {args.host}:{args.port}. Check host/port.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n[!] HTTP Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)
    finally:
        try:
            client.logout()
        except:
            pass


if __name__ == "__main__":
    main()
