# Nessus Bulk Downloader

Automates bulk downloading of Tenable Nessus scan results across all IPs/scans, eliminating the need to manually download files one-by-one.

## Problem Solved

When conducting a Network VA with 100 IPs, you'd need to manually download 300+ files (100 `.nessus` + 100 `.html` + 100 `.csv`). This tool automates the entire process in minutes.

## Features

- **Bulk export**: Download all scans in `.nessus`, `.html`, `.csv`, `.pdf`, `.db` formats simultaneously
- **Parallel downloads**: Configurable workers (up to 10) to speed up the process
- **Selective scanning**: Choose specific scans or filter by folder
- **Two auth methods**: API keys (recommended) or username/password
- **Web UI**: Browser-based dashboard with real-time progress logs
- **CLI mode**: Scriptable command-line interface for automation/CI pipelines
- **Download report**: JSON report of all download results saved automatically
- **Smart skipping**: Automatically skips scans that aren't in `completed`/`imported` state

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Usage — Web UI (Recommended)

```bash
python nessus_web_ui.py
```

Then open **http://localhost:5000** in your browser.

1. Enter your Nessus host and credentials
2. Click **Test Connection** — your scans will load automatically
3. Select which scans to download (all completed scans are pre-selected)
4. Choose formats and output directory
5. Click **Start Bulk Download** and watch the live log

---

## Usage — Command Line

### Basic (API Keys, all scans, default formats)
```bash
python nessus_downloader.py \
  --host 192.168.1.100 \
  --access-key YOUR_ACCESS_KEY \
  --secret-key YOUR_SECRET_KEY
```

### Username/Password, specific scans
```bash
python nessus_downloader.py \
  --host 192.168.1.100 \
  --username admin \
  --password yourpassword \
  --scan-ids 10 11 12 15 20
```

### Custom formats and output directory
```bash
python nessus_downloader.py \
  --host 192.168.1.100 \
  --access-key KEY \
  --secret-key SECRET \
  --formats nessus html csv \
  --output-dir /evidence/client_name/VA_2025 \
  --workers 5
```

### Filter by folder
```bash
python nessus_downloader.py \
  --host 192.168.1.100 \
  --access-key KEY \
  --secret-key SECRET \
  --folder-id 3 \
  --formats nessus html
```

---

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | required | Nessus host/IP |
| `--port` | 8834 | Nessus port |
| `--access-key` | — | API access key |
| `--secret-key` | — | API secret key |
| `--username` / `-u` | — | Login username |
| `--password` / `-p` | — | Login password |
| `--formats` | nessus html csv | Space-separated formats |
| `--scan-ids` | all | Specific scan IDs |
| `--folder-id` | all | Filter by folder |
| `--output-dir` | ./nessus_downloads | Where to save files |
| `--workers` | 3 | Parallel workers |
| `--verify-ssl` | false | Verify SSL cert |

---

## Output Structure

```
nessus_downloads/
├── Scan_Name_1.nessus
├── Scan_Name_1.html
├── Scan_Name_1.csv
├── Scan_Name_2.nessus
├── Scan_Name_2.html
└── Scan_Name_2.csv
...
└── download_report_20250512_143022.json
```

---

## Getting Nessus API Keys

1. Log into Nessus web UI
2. Click your username (top right) → **My Account**
3. Under **API Keys** section → **Generate**
4. Copy the Access Key and Secret Key

---

## Notes

- SSL verification is disabled by default (Nessus uses self-signed certs). Use `--verify-ssl` if you have a valid cert.
- Only scans with `completed` or `imported` status are downloaded.
- The export process involves: request export → poll for ready → download. This is the standard Nessus API flow.
- PDF export requires Nessus Professional or higher.
