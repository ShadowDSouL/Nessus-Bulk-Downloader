# Nessus Bulk Downloader

Automates bulk downloading of Tenable Nessus scan results across all IPs/scans, eliminating the need to manually download files one by one.

## Problem Solved

When conducting a Network VA with 100 IPs, you would need to manually download 300+ files (100 `.nessus` + 100 `.html` + 100 `.csv`). This tool automates the entire process in minutes.

---

## Features

- **Bulk export** — Download all scans in `.nessus`, `.html`, `.csv`, `.pdf`, `.db` formats simultaneously
- **Parallel downloads** — Configurable workers (up to 10) to speed up the process
- **Selective download** — Cherry-pick specific scans or filter by folder
- **Folder filter** — Filter scan list by Nessus folder, updates scan list instantly
- **Refresh button** — Refresh scan list without re-entering credentials (picks up newly completed scans)
- **Two auth methods** — API keys (recommended) or username/password
- **Web UI** — Browser-based dashboard with real-time colour-coded live log
- **CLI mode** — Scriptable command-line interface for automation
- **Standalone binary** — Single executable for Linux, no Python or pip required on target machine
- **Smart skipping** — Automatically skips scans not in `completed`/`imported` state
- **License detection** — Gracefully skips PDF/DB exports when not supported by your Nessus license
- **Download report** — JSON summary of all results saved automatically after each run

---

## What's Inside the Zip

```
nessus-bulk-downloader.zip
├── nessus-bulk-downloader      # Standalone Linux binary (no install needed)
├── nessus_bulk_downloader.py   # Single-file Python source (Web UI + CLI)
├── requirements.txt            # Python dependencies
├── start_webui.sh              # Linux/macOS launcher
├── start_webui.bat             # Windows launcher
└── README.md
```

---

## Installation

### Option A — Standalone Binary (Linux, no install needed)

No Python, no pip, nothing to install. Just copy and run.

```bash
chmod +x nessus-bulk-downloader
./nessus-bulk-downloader
```

Browser opens automatically at **http://localhost:5000**.

### Option B — Python (Linux / macOS / Windows)

Requires Python 3.8 or higher.

```bash
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
bash start_webui.sh
```

**Windows:**
```
Double-click start_webui.bat
```

Or run manually:
```bash
# Linux / macOS
python3 nessus_bulk_downloader.py

# Windows
python nessus_bulk_downloader.py
```

Then open **http://localhost:5000** in your browser.

---

## Deployment Scenarios

### Scenario 1 — Your own machine, Nessus on client's machine (same network / VPN)

Run the tool on your machine and point it at the client's Nessus IP.

```
Host: 192.168.1.100    (client's Nessus IP)
Port: 8834
```

### Scenario 2 — Nessus behind a firewall, accessible via SSH tunnel

```bash
# Forward client's Nessus port to your machine first
ssh -L 8834:localhost:8834 user@client-machine-ip

# Then in the tool use
Host: 127.0.0.1
Port: 8834
```

### Scenario 3 — You are physically at the client's Linux machine (no install allowed)

Copy the standalone binary via USB or SCP — nothing to install.

```bash
# Copy to client machine
scp nessus-bulk-downloader user@client:/tmp/

# On the client machine — just run it
chmod +x /tmp/nessus-bulk-downloader
/tmp/nessus-bulk-downloader
# Browser opens at http://localhost:5000
```

### Scenario 4 — Client's machine is Windows (no install allowed)

Build a Windows .exe on any Windows machine with Python installed:

```
pip install pyinstaller flask requests
pyinstaller --onefile nessus_bulk_downloader.py
```

This produces `dist/nessus_bulk_downloader.exe` — copy it to the client's machine and double-click. No installation required.

---

## Usage — Web UI (Recommended)

1. Enter your Nessus **Host / IP** and **Port** (default: 8834)
2. Choose your auth method — **API Keys** or **Username/Password**
3. Click **Test Connection** — scan list loads automatically
4. Use the **Folder Filter** dropdown to narrow down scans if needed
5. Click **Refresh** anytime to pick up newly completed scans without reconnecting
6. Select which scans to download (all completed scans are pre-ticked)
7. Choose your **Export Formats** — `.nessus`, `.html`, `.csv`, `.pdf`, `.db`
8. Set your **Output Directory** and **Parallel Workers**
9. Click **Start Bulk Download** and watch the live log

### Live Log Colours

| Colour | Meaning |
|--------|---------|
| Green  | File saved successfully |
| Red    | Hard error / download failed |
| Orange | Skipped (license limitation or scan not ready) |
| Cyan   | Progress info (requesting, waiting, downloading) |
| Grey   | General status messages |

---

## Usage — CLI Mode

Append `--cli` as the first argument to run without the Web UI.

### Basic — API keys, all scans, default formats
```bash
./nessus-bulk-downloader --cli \
  --host 192.168.1.100 \
  --access-key YOUR_ACCESS_KEY \
  --secret-key YOUR_SECRET_KEY
```

### Username/Password, specific scan IDs
```bash
./nessus-bulk-downloader --cli \
  --host 192.168.1.100 \
  --username admin \
  --password yourpassword \
  --scan-ids 10 11 12 15 20
```

### Custom formats, output directory, and workers
```bash
./nessus-bulk-downloader --cli \
  --host 192.168.1.100 \
  --access-key KEY \
  --secret-key SECRET \
  --formats nessus html csv \
  --output-dir /evidence/ClientName_VA_2025 \
  --workers 5
```

### Filter by folder
```bash
./nessus-bulk-downloader --cli \
  --host 192.168.1.100 \
  --access-key KEY \
  --secret-key SECRET \
  --folder-id 3 \
  --formats nessus html
```

> When using the Python source instead of the binary, replace `./nessus-bulk-downloader` with `python3 nessus_bulk_downloader.py`

---

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | required | Nessus host / IP |
| `--port` | 8834 | Nessus port |
| `--access-key` | — | API access key |
| `--secret-key` | — | API secret key |
| `--username` / `-u` | — | Login username |
| `--password` / `-p` | — | Login password |
| `--formats` | nessus html csv | One or more: nessus html csv pdf db |
| `--scan-ids` | all | Specific scan IDs to download |
| `--folder-id` | all | Filter scans by folder ID |
| `--output-dir` | ./nessus_downloads | Where to save files |
| `--workers` | 3 | Parallel download workers |
| `--verify-ssl` | false | Verify SSL certificate |

---

## Output Structure

All files are saved flat into the output directory — no subfolders per scan.

```
nessus_downloads/
├── Scan_Name_1.nessus
├── Scan_Name_1.html
├── Scan_Name_1.csv
├── Scan_Name_2.nessus
├── Scan_Name_2.html
├── Scan_Name_2.csv
...
└── download_report_20250513_143022.json
```

The `download_report_*.json` file is saved automatically after every run and contains a full summary of what succeeded, failed, or was skipped.

---

## Getting Nessus API Keys

1. Log into the Nessus web UI
2. Click your username (top right) → **My Account**
3. Under **API Keys** → click **Generate**
4. Copy both the **Access Key** and **Secret Key**

API keys are preferred over username/password as they do not expire with the session.

---

## Notes

- SSL verification is disabled by default as Nessus typically uses self-signed certificates. Use `--verify-ssl` if you have a valid cert.
- Only scans with `completed` or `imported` status are downloaded. Others are automatically skipped.
- PDF and DB export require **Nessus Professional** or **Tenable.io**. On Nessus Essentials (free), these formats are blocked by the API and will be gracefully skipped with an orange warning in the log.
- The HTML report includes: Vulnerability Hosts Summary, Vulnerability by Host, Compliance Executive Summary, and Compliance. Plugin details and Remediations are excluded.
- The export flow follows the standard Nessus API: request export → poll until ready → download.
