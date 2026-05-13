#!/bin/bash
echo ""
echo "============================================"
echo "  Nessus Bulk Downloader - Web UI"
echo "============================================"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 not found. Install it with: sudo apt install python3"
    exit 1
fi

echo "Checking dependencies..."
pip3 install -r requirements.txt -q

echo ""
echo "Starting server... Open http://localhost:5000 in your browser"
echo "Press Ctrl+C to stop."
echo ""
python3 nessus_bulk_downloader.py
