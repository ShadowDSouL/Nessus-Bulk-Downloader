#!/usr/bin/env python3
"""
Nessus Bulk Downloader - Standalone Entry Point
Bundles both CLI and Web UI into a single executable.
Usage:
  nessus-bulk-downloader             -> launches Web UI on http://localhost:5000
  nessus-bulk-downloader --cli ...   -> runs CLI mode
  nessus-bulk-downloader --help      -> shows help
"""

import sys
import os

# When running as PyInstaller bundle, fix paths
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Embedded HTML (inlined so no templates/ folder needed in the exe) ─────────
EMBEDDED_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nessus Bulk Downloader</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0a0c10; --bg2: #111318; --bg3: #181c24;
    --border: #1e2330; --border2: #2a3040;
    --text: #e2e8f0; --text2: #8892a4; --text3: #525d70;
    --accent: #00d4ff; --accent2: #0099bb;
    --green: #00ff88; --red: #ff4466; --amber: #ff8c00;
    --mono: 'JetBrains Mono', monospace; --sans: 'Syne', sans-serif;
  }
  body { background:var(--bg); color:var(--text); font-family:var(--mono); min-height:100vh; font-size:13px; line-height:1.6; }
  .topbar { border-bottom:1px solid var(--border); padding:0 32px; height:56px; display:flex; align-items:center; gap:16px; position:sticky; top:0; z-index:100; background:var(--bg); }
  .logo { font-family:var(--sans); font-weight:800; font-size:15px; letter-spacing:-0.02em; color:var(--accent); display:flex; align-items:center; gap:10px; }
  .logo-icon { width:28px; height:28px; border:1.5px solid var(--accent); border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:14px; }
  .badge { background:var(--bg3); border:1px solid var(--border2); color:var(--text3); font-size:10px; padding:2px 8px; border-radius:3px; letter-spacing:0.1em; text-transform:uppercase; }
  .main { max-width:1100px; margin:0 auto; padding:32px; display:grid; grid-template-columns:380px 1fr; gap:24px; align-items:start; }
  .panel { background:var(--bg2); border:1px solid var(--border); border-radius:10px; overflow:hidden; }
  .panel-header { padding:14px 20px; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:10px; font-family:var(--sans); font-size:12px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:var(--text2); }
  .panel-header .dot { width:6px; height:6px; border-radius:50%; background:var(--accent); box-shadow:0 0 6px var(--accent); }
  .panel-body { padding:20px; }
  .field { margin-bottom:14px; }
  .field label { display:block; font-size:10px; letter-spacing:0.1em; text-transform:uppercase; color:var(--text3); margin-bottom:6px; font-family:var(--sans); font-weight:600; }
  .field input, .field select { width:100%; background:var(--bg3); border:1px solid var(--border2); border-radius:6px; padding:9px 12px; color:var(--text); font-family:var(--mono); font-size:13px; outline:none; transition:border-color 0.15s; }
  .field input:focus, .field select:focus { border-color:var(--accent2); }
  .field input::placeholder { color:var(--text3); }
  .field select option { background:var(--bg3); }
  .row { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
  .auth-tabs { display:flex; border:1px solid var(--border2); border-radius:6px; overflow:hidden; margin-bottom:14px; }
  .auth-tab { flex:1; padding:8px; background:transparent; border:none; color:var(--text3); cursor:pointer; font-family:var(--mono); font-size:11px; transition:all 0.15s; text-align:center; }
  .auth-tab.active { background:var(--accent); color:var(--bg); font-weight:700; }
  .format-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
  .format-btn { padding:10px 6px; background:var(--bg3); border:1px solid var(--border2); border-radius:6px; color:var(--text2); cursor:pointer; font-family:var(--mono); font-size:11px; text-align:center; transition:all 0.15s; display:flex; flex-direction:column; align-items:center; gap:4px; }
  .format-btn .fmt-icon { font-size:16px; }
  .format-btn.selected { border-color:var(--accent); color:var(--accent); background:rgba(0,212,255,0.06); }
  .btn { width:100%; padding:12px; border-radius:7px; border:none; cursor:pointer; font-family:var(--sans); font-weight:600; font-size:13px; letter-spacing:0.04em; transition:all 0.15s; }
  .btn-test { background:transparent; border:1px solid var(--border2); color:var(--text2); margin-bottom:10px; }
  .btn-test:hover { border-color:var(--accent2); color:var(--accent); }
  .btn-start { background:var(--accent); color:var(--bg); }
  .btn-start:hover { background:var(--accent2); }
  .btn-start:disabled { opacity:0.4; cursor:not-allowed; }
  .connection-status { padding:10px 14px; border-radius:6px; font-size:12px; margin-bottom:14px; display:none; }
  .status-ok { background:rgba(0,255,136,0.07); border:1px solid rgba(0,255,136,0.25); color:var(--green); }
  .status-err { background:rgba(255,68,102,0.07); border:1px solid rgba(255,68,102,0.25); color:var(--red); }
  .right-col { display:flex; flex-direction:column; gap:20px; }
  .stats-row { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
  .stat-card { background:var(--bg2); border:1px solid var(--border); border-radius:8px; padding:14px 16px; }
  .stat-label { font-size:10px; letter-spacing:0.1em; text-transform:uppercase; color:var(--text3); font-family:var(--sans); margin-bottom:6px; }
  .stat-value { font-size:28px; font-weight:700; font-family:var(--sans); line-height:1; }
  .stat-value.green { color:var(--green); }
  .stat-value.red { color:var(--red); }
  .stat-value.cyan { color:var(--accent); }
  .log-container { background:var(--bg); border:1px solid var(--border); border-radius:8px; height:340px; overflow-y:auto; padding:16px; font-size:12px; line-height:1.8; }
  .log-line { color:var(--text2); }
  .log-line.ok { color:#00ff88; }
  .log-line.err { color:#ff4466; }
  .log-line.info { color:#00d4ff; }
  .log-line.warn { color:#ff8c00; }
  .scan-list { max-height:280px; overflow-y:auto; }
  .scan-item { padding:10px 14px; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:10px; cursor:pointer; transition:background 0.1s; }
  .scan-item:hover { background:var(--bg3); }
  .scan-item:last-child { border-bottom:none; }
  .scan-check { width:16px; height:16px; border:1px solid var(--border2); border-radius:3px; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:10px; transition:all 0.1s; }
  .scan-item.selected .scan-check { background:var(--accent); border-color:var(--accent); color:var(--bg); }
  .scan-info { flex:1; min-width:0; }
  .scan-name { color:var(--text); font-size:12px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .scan-meta { color:var(--text3); font-size:10px; }
  .scan-status { font-size:9px; padding:2px 7px; border-radius:3px; text-transform:uppercase; letter-spacing:0.06em; font-family:var(--sans); font-weight:600; }
  .s-completed { background:rgba(0,255,136,0.1); color:var(--green); border:1px solid rgba(0,255,136,0.2); }
  .s-running { background:rgba(0,212,255,0.1); color:var(--accent); border:1px solid rgba(0,212,255,0.2); }
  .s-other { background:var(--bg3); color:var(--text3); border:1px solid var(--border); }
  .job-bar { height:4px; background:var(--bg3); border-radius:2px; overflow:hidden; margin-bottom:4px; }
  .job-bar-fill { height:100%; background:linear-gradient(90deg,var(--accent),var(--green)); border-radius:2px; transition:width 0.5s; width:0%; }
  .job-bar-fill.done { width:100% !important; }
  .select-all-row { display:flex; justify-content:space-between; align-items:center; padding:8px 14px; border-bottom:1px solid var(--border); }
  .link-btn { background:none; border:none; color:var(--accent2); cursor:pointer; font-size:11px; font-family:var(--mono); }
  .link-btn:hover { color:var(--accent); }
  ::-webkit-scrollbar { width:4px; }
  ::-webkit-scrollbar-track { background:transparent; }
  ::-webkit-scrollbar-thumb { background:var(--border2); border-radius:2px; }
</style>
</head>
<body>
<div class="topbar">
  <div class="logo"><div class="logo-icon">&#x2B21;</div>Nessus Bulk Downloader</div>
  <div class="badge">v1.0</div>
  <div style="margin-left:auto;color:var(--text3);font-size:11px;">Network VA Automation</div>
</div>
<div class="main">
  <div style="display:flex;flex-direction:column;gap:16px;">
    <div class="panel">
      <div class="panel-header"><div class="dot"></div>Connection</div>
      <div class="panel-body">
        <div class="row">
          <div class="field"><label>Host / IP</label><input type="text" id="host" placeholder="192.168.1.100"></div>
          <div class="field"><label>Port</label><input type="text" id="port" value="8834"></div>
        </div>
        <div class="auth-tabs">
          <button class="auth-tab active" onclick="switchAuth('apikey')">API Keys</button>
          <button class="auth-tab" onclick="switchAuth('password')">Username/Password</button>
        </div>
        <div id="auth-apikey">
          <div class="field"><label>Access Key</label><input type="text" id="access_key" placeholder="xxxxxxxxxxxxxxxx"></div>
          <div class="field"><label>Secret Key</label><input type="password" id="secret_key" placeholder="xxxxxxxxxxxxxxxx"></div>
        </div>
        <div id="auth-password" style="display:none">
          <div class="field"><label>Username</label><input type="text" id="username" placeholder="admin"></div>
          <div class="field"><label>Password</label><input type="password" id="password"></div>
        </div>
        <div id="conn-status" class="connection-status"></div>
        <button class="btn btn-test" onclick="testConnection()">&#x2B21; Test Connection</button>
      </div>
    </div>
    <div class="panel">
      <div class="panel-header"><div class="dot"></div>Download Options</div>
      <div class="panel-body">
        <div class="field">
          <label>Export Formats</label>
          <div class="format-grid">
            <div class="format-btn selected" data-fmt="nessus" onclick="toggleFormat(this)"><span class="fmt-icon">&#x1F5C4;</span>.nessus</div>
            <div class="format-btn selected" data-fmt="html" onclick="toggleFormat(this)"><span class="fmt-icon">&#x1F310;</span>.html</div>
            <div class="format-btn selected" data-fmt="csv" onclick="toggleFormat(this)"><span class="fmt-icon">&#x1F4CA;</span>.csv</div>
            <div class="format-btn" data-fmt="pdf" onclick="toggleFormat(this)"><span class="fmt-icon">&#x1F4C4;</span>.pdf</div>
            <div class="format-btn" data-fmt="db" onclick="toggleFormat(this)"><span class="fmt-icon">&#x1F4BE;</span>.db</div>
          </div>
        </div>
        <div class="field"><label>Output Directory</label><input type="text" id="output_dir" value="./nessus_downloads"></div>
        <div class="row">
          <div class="field"><label>Parallel Workers</label>
            <select id="workers">
              <option value="1">1 (slow)</option><option value="2">2</option>
              <option value="3" selected>3 (default)</option><option value="5">5</option><option value="10">10 (fast)</option>
            </select>
          </div>
          <div class="field"><label>Folder Filter</label><select id="folder_id"><option value="">All folders</option></select></div>
        </div>
        <button class="btn btn-start" id="btn-start" onclick="startDownload()" disabled>&#x25B6; Start Bulk Download</button>
      </div>
    </div>
  </div>
  <div class="right-col">
    <div class="stats-row">
      <div class="stat-card"><div class="stat-label">Total Scans</div><div class="stat-value cyan" id="stat-total">-</div></div>
      <div class="stat-card"><div class="stat-label">Selected</div><div class="stat-value cyan" id="stat-selected">-</div></div>
      <div class="stat-card"><div class="stat-label">Success</div><div class="stat-value green" id="stat-success">-</div></div>
      <div class="stat-card"><div class="stat-label">Failed</div><div class="stat-value red" id="stat-failed">-</div></div>
    </div>
    <div class="panel">
      <div class="panel-header">
        <div class="dot"></div>Scan List
        <span id="scan-count" style="margin-left:auto;color:var(--text3);font-size:11px;">Connect to load</span>
        <button id="btn-refresh" onclick="refreshScans()" style="display:none;margin-left:10px;background:transparent;border:1px solid var(--border2);color:var(--text3);border-radius:4px;padding:3px 9px;cursor:pointer;font-size:11px;font-family:var(--mono);">&#x21BB; Refresh</button>
      </div>
      <div class="select-all-row" id="select-all-row" style="display:none">
        <span style="color:var(--text3);font-size:11px;">Select scans to download</span>
        <div><button class="link-btn" onclick="selectAll()">Select all</button> &nbsp;&#xB7;&nbsp; <button class="link-btn" onclick="deselectAll()">Deselect all</button></div>
      </div>
      <div class="scan-list" id="scan-list"><div style="padding:40px;text-align:center;color:var(--text3);font-family:var(--sans)">Connect to Nessus to see available scans</div></div>
    </div>
    <div class="panel">
      <div class="panel-header">
        <div class="dot"></div>Live Log
        <span id="job-status-badge" style="margin-left:auto;font-size:10px;color:var(--text3);">IDLE</span>
      </div>
      <div class="panel-body" style="padding:0">
        <div class="job-bar" style="margin:0;border-radius:0;"><div class="job-bar-fill" id="job-bar-fill"></div></div>
        <div class="log-container" id="log-container"><div style="color:var(--text3);text-align:center;margin-top:120px;font-family:var(--sans)">Waiting for job to start...</div></div>
      </div>
    </div>
  </div>
</div>
<script>
let authMode='apikey', allScans=[], selectedScanIds=new Set(), activeJobId=null, pollInterval=null, connectedFolders=[];
function switchAuth(mode){authMode=mode;document.querySelectorAll('.auth-tab').forEach(t=>t.classList.remove('active'));event.target.classList.add('active');document.getElementById('auth-apikey').style.display=mode==='apikey'?'':'none';document.getElementById('auth-password').style.display=mode==='password'?'':'none';}
function toggleFormat(el){el.classList.toggle('selected');}
function getConfig(){
  const formats=[];document.querySelectorAll('.format-btn.selected').forEach(b=>formats.push(b.dataset.fmt));
  const cfg={host:document.getElementById('host').value.trim(),port:document.getElementById('port').value.trim()||'8834',formats,output_dir:document.getElementById('output_dir').value.trim()||'./nessus_downloads',workers:document.getElementById('workers').value,folder_id:document.getElementById('folder_id').value||null};
  if(authMode==='apikey'){cfg.access_key=document.getElementById('access_key').value.trim();cfg.secret_key=document.getElementById('secret_key').value.trim();}
  else{cfg.username=document.getElementById('username').value.trim();cfg.password=document.getElementById('password').value;}
  if(selectedScanIds.size>0)cfg.scan_ids=[...selectedScanIds];
  return cfg;
}
async function testConnection(){
  const cfg=getConfig();if(!cfg.host){showConnStatus('Enter a host/IP',false);return;}
  const s=document.getElementById('conn-status');s.className='connection-status status-ok';s.style.display='block';s.textContent='Connecting...';
  try{
    const res=await fetch('/api/test-connection',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cfg)});
    const data=await res.json();
    if(data.ok){
      s.className='connection-status status-ok';s.textContent='Connected - '+data.scan_count+' scan(s) found';
      document.getElementById('btn-start').disabled=false;document.getElementById('btn-refresh').style.display='';
      allScans=data.scans||[];connectedFolders=data.folders||[];
      renderScans(allScans);renderFolders(connectedFolders);
      document.getElementById('stat-total').textContent=allScans.length;
    }else{s.className='connection-status status-err';s.textContent='Error: '+data.error;}
  }catch(e){s.className='connection-status status-err';s.textContent='Network error: '+e.message;}
}
async function refreshScans(){
  const btn=document.getElementById('btn-refresh');btn.innerHTML='...';btn.disabled=true;
  try{
    const res=await fetch('/api/test-connection',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(getConfig())});
    const data=await res.json();
    if(data.ok){allScans=data.scans||[];selectedScanIds.clear();filterScansByFolder();document.getElementById('stat-total').textContent=allScans.length;btn.style.color='var(--green)';btn.innerHTML='Done';setTimeout(()=>{btn.style.color='';btn.innerHTML='&#x21BB; Refresh';btn.disabled=false;},1200);}
    else{btn.innerHTML='Error';setTimeout(()=>{btn.innerHTML='&#x21BB; Refresh';btn.disabled=false;},1500);}
  }catch(e){btn.innerHTML='Error';setTimeout(()=>{btn.innerHTML='&#x21BB; Refresh';btn.disabled=false;},1500);}
}
function renderFolders(folders){
  const sel=document.getElementById('folder_id');sel.innerHTML='<option value="">All folders</option>';
  folders.forEach(f=>{const o=document.createElement('option');o.value=f.id;o.textContent=f.name;sel.appendChild(o);});
  sel.onchange=()=>filterScansByFolder();
}
function filterScansByFolder(){
  const fid=document.getElementById('folder_id').value;selectedScanIds.clear();
  const filtered=fid?allScans.filter(s=>String(s.folder_id)===String(fid)):allScans;
  renderScans(filtered);document.getElementById('stat-total').textContent=filtered.length;
}
function renderScans(scans){
  document.getElementById('select-all-row').style.display='flex';
  document.getElementById('scan-count').textContent=scans.length+' scans';
  const el=document.getElementById('scan-list');
  if(!scans.length){el.innerHTML='<div style="padding:30px;text-align:center;color:var(--text3)">No scans found</div>';return;}
  el.innerHTML='';
  scans.forEach(scan=>{
    const status=(scan.status||'unknown').toLowerCase();
    const ok=['completed','imported'].includes(status);
    const div=document.createElement('div');
    div.className='scan-item'+(ok?' selected':'');div.dataset.id=scan.id;
    const sc=status==='completed'?'s-completed':status==='running'?'s-running':'s-other';
    const ts=scan.last_modification_date?new Date(scan.last_modification_date*1000).toLocaleDateString():'-';
    div.innerHTML=`<div class="scan-check">${ok?'&#x2713;':''}</div><div class="scan-info"><div class="scan-name">${scan.name||'Unnamed'}</div><div class="scan-meta">ID: ${scan.id} &middot; Modified: ${ts}</div></div><span class="scan-status ${sc}">${status}</span>`;
    if(ok){selectedScanIds.add(scan.id);div.onclick=()=>toggleScan(div,scan.id);}
    el.appendChild(div);
  });
  updateSelectedCount();
}
function toggleScan(el,id){if(selectedScanIds.has(id)){selectedScanIds.delete(id);el.classList.remove('selected');el.querySelector('.scan-check').innerHTML='';}else{selectedScanIds.add(id);el.classList.add('selected');el.querySelector('.scan-check').innerHTML='&#x2713;';}updateSelectedCount();}
function selectAll(){document.querySelectorAll('.scan-item').forEach(el=>{const id=parseInt(el.dataset.id);const scan=allScans.find(s=>s.id===id);if(scan&&['completed','imported'].includes((scan.status||'').toLowerCase())){selectedScanIds.add(id);el.classList.add('selected');el.querySelector('.scan-check').innerHTML='&#x2713;';}});updateSelectedCount();}
function deselectAll(){selectedScanIds.clear();document.querySelectorAll('.scan-item').forEach(el=>{el.classList.remove('selected');el.querySelector('.scan-check').innerHTML='';});updateSelectedCount();}
function updateSelectedCount(){document.getElementById('stat-selected').textContent=selectedScanIds.size;}
async function startDownload(){
  if(selectedScanIds.size===0){alert('Select at least one scan.');return;}
  const cfg=getConfig();if(cfg.formats.length===0){alert('Select at least one format.');return;}
  document.getElementById('btn-start').disabled=true;document.getElementById('log-container').innerHTML='';
  document.getElementById('stat-success').textContent='0';document.getElementById('stat-failed').textContent='0';
  document.getElementById('job-status-badge').textContent='RUNNING';document.getElementById('job-status-badge').style.color='var(--accent)';
  document.getElementById('job-bar-fill').classList.remove('done');document.getElementById('job-bar-fill').style.width='5%';
  try{
    const res=await fetch('/api/start-download',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(cfg)});
    const data=await res.json();activeJobId=data.job_id;pollJob();
  }catch(e){appendLog('Failed to start: '+e.message,'err');document.getElementById('btn-start').disabled=false;}
}
function pollJob(){
  if(pollInterval)clearInterval(pollInterval);
  pollInterval=setInterval(async()=>{
    if(!activeJobId)return;
    try{
      const res=await fetch('/api/job/'+activeJobId);const job=await res.json();
      renderLogs(job.logs||[]);
      const total=selectedScanIds.size,done=(job.results?.success?.length||0)+(job.results?.failed?.length||0);
      document.getElementById('job-bar-fill').style.width=Math.min(95,total>0?Math.round(done/total*100):5)+'%';
      if(job.results){document.getElementById('stat-success').textContent=job.results.success?.length||0;document.getElementById('stat-failed').textContent=job.results.failed?.length||0;}
      if(job.status==='done'||job.status==='error'){
        clearInterval(pollInterval);document.getElementById('job-bar-fill').classList.add('done');
        document.getElementById('job-status-badge').textContent=job.status==='done'?'DONE':'ERROR';
        document.getElementById('job-status-badge').style.color=job.status==='done'?'var(--green)':'var(--red)';
        document.getElementById('btn-start').disabled=false;
      }
    }catch(e){}
  },1000);
}
let lastLogCount=0;
function classifyLog(line){
  const l=line.toLowerCase();
  if((line.includes('saved')&&line.includes('KB'))||line.includes('Done!')&&line.includes('Success')||line.includes('Connected'))return'ok';
  if(line.includes('!!')&&(l.includes('skipped')||l.includes('not supported'))||l.includes('skipping')||l.includes('timeout'))return'warn';
  if(line.includes('!'))if(l.includes('skipped')||l.includes('not supported'))return'warn';
  if(line.includes('Failed')||l.includes('error')||line.includes('timed out'))return'err';
  if(l.includes('requesting')||l.includes('waiting')||l.includes('downloading')||l.includes('fetching')||l.includes('connecting')||line.includes('Report saved'))return'info';
  return'';
}
function renderLogs(logs){
  if(logs.length===lastLogCount)return;lastLogCount=logs.length;
  const c=document.getElementById('log-container');c.innerHTML='';
  logs.forEach(line=>{const d=document.createElement('div');const cls=classifyLog(line);d.className=cls?'log-line '+cls:'log-line';d.textContent=line;c.appendChild(d);});
  c.scrollTop=c.scrollHeight;
}
</script>
</body>
</html>
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import json
import threading
import time
import webbrowser
import requests
import urllib3
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from flask import Flask, request, jsonify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ── Nessus API Client ─────────────────────────────────────────────────────────
class NessusClient:
    def __init__(self, host, port, username=None, password=None,
                 access_key=None, secret_key=None, verify_ssl=False):
        self.base_url = f"https://{host}:{port}"
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.token = None

        if access_key and secret_key:
            self.session.headers.update({
                "X-ApiKeys": f"accessKey={access_key}; secretKey={secret_key}",
                "Content-Type": "application/json", "Accept": "application/json"
            })
            self.auth_method = "api_keys"
        elif username and password:
            self.username = username
            self.password = password
            self.auth_method = "password"
            self._login()
        else:
            raise ValueError("Provide API keys or username/password")

    def _login(self):
        r = self.session.post(f"{self.base_url}/session",
                              json={"username": self.username, "password": self.password})
        r.raise_for_status()
        self.token = r.json()["token"]
        self.session.headers.update({
            "X-Cookie": f"token={self.token}",
            "Content-Type": "application/json", "Accept": "application/json"
        })

    def logout(self):
        if self.auth_method == "password" and self.token:
            try: self.session.delete(f"{self.base_url}/session")
            except: pass

    def get_scans(self, folder_id=None):
        params = {"folder_id": folder_id} if folder_id else {}
        r = self.session.get(f"{self.base_url}/scans", params=params)
        r.raise_for_status()
        return r.json().get("scans", []) or []

    def get_folders(self):
        r = self.session.get(f"{self.base_url}/folders")
        r.raise_for_status()
        return r.json().get("folders", []) or []

    def export_scan(self, scan_id, fmt, chapters=None):
        payload = {"format": fmt}
        if fmt == "html" and chapters:
            payload["chapters"] = chapters
        elif fmt == "csv":
            payload["reportContents"] = {"csvColumns": {
                "id": True, "cve": True, "cvss": True, "risk": True,
                "hostname": True, "protocol": True, "port": True,
                "plugin_name": True, "synopsis": True, "description": True,
                "solution": True, "see_also": True, "plugin_output": True
            }}
        r = self.session.post(f"{self.base_url}/scans/{scan_id}/export", json=payload)
        r.raise_for_status()
        return r.json()["file"]

    def check_export_status(self, scan_id, file_id):
        r = self.session.get(f"{self.base_url}/scans/{scan_id}/export/{file_id}/status")
        r.raise_for_status()
        return r.json()["status"]

    def download_export(self, scan_id, file_id):
        r = self.session.get(f"{self.base_url}/scans/{scan_id}/export/{file_id}/download", stream=True)
        r.raise_for_status()
        return r.content

    def wait_for_export(self, scan_id, file_id, timeout=300):
        start = time.time()
        while time.time() - start < timeout:
            status = self.check_export_status(scan_id, file_id)
            if status == "ready": return True
            if status == "error": return False
            time.sleep(2)
        return False


# ── Bulk Downloader ───────────────────────────────────────────────────────────
class BulkDownloader:
    def __init__(self, client, output_dir, formats, max_workers=3, log_callback=None):
        self.client = client
        self.output_dir = Path(output_dir)
        self.formats = formats
        self.max_workers = max_workers
        self.log = log_callback or print
        self.results = {"success": [], "failed": [], "skipped": []}

    def sanitize_name(self, name):
        for ch in '<>:"/\\|?*': name = name.replace(ch, "_")
        return name.strip()[:100]

    def download_scan(self, scan):
        scan_id = scan["id"]
        scan_name = self.sanitize_name(scan.get("name", f"scan_{scan_id}"))
        result = {"scan_id": scan_id, "scan_name": scan_name, "formats": {}}

        for fmt in self.formats:
            try:
                self.log(f"[{scan_name}] Requesting {fmt.upper()} export...")
                chapters = "vuln_hosts_summary;vuln_by_host;compliance_exec;compliance" if fmt == "html" else None
                try:
                    file_id = self.client.export_scan(scan_id, fmt, chapters)
                except requests.exceptions.HTTPError as he:
                    if he.response is not None and he.response.status_code == 400:
                        result["formats"][fmt] = {"status": "license_required", "error": f"{fmt.upper()} not supported on this license"}
                        self.log(f"[{scan_name}] ! {fmt.upper()} skipped - not supported on this Nessus license")
                        continue
                    raise

                self.log(f"[{scan_name}] Waiting for {fmt.upper()} export (file: {file_id})...")
                ready = self.client.wait_for_export(scan_id, file_id)
                if not ready:
                    result["formats"][fmt] = {"status": "timeout"}
                    self.log(f"[{scan_name}] ! {fmt.upper()} timed out")
                    continue

                self.log(f"[{scan_name}] Downloading {fmt.upper()}...")
                content = self.client.download_export(scan_id, file_id)
                ext = {"nessus": ".nessus", "html": ".html", "csv": ".csv", "pdf": ".pdf", "db": ".db"}.get(fmt, f".{fmt}")
                filepath = self.output_dir / f"{scan_name}{ext}"
                filepath.write_bytes(content)
                size_kb = round(len(content) / 1024, 1)
                result["formats"][fmt] = {"status": "ok", "path": str(filepath), "size_kb": size_kb}
                self.log(f"[{scan_name}] {fmt.upper()} saved ({size_kb} KB) -> {filepath}")

            except Exception as e:
                result["formats"][fmt] = {"status": "error", "error": str(e)}
                self.log(f"[{scan_name}] Failed {fmt.upper()}: {e}")

        return result

    def run(self, scan_ids=None, folder_id=None):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log("Fetching scan list from Nessus...")
        all_scans = self.client.get_scans(folder_id)
        if not all_scans:
            self.log("No scans found.")
            return self.results

        scans = [s for s in all_scans if s["id"] in scan_ids] if scan_ids else all_scans
        completed = [s for s in scans if s.get("status", "").lower() in {"completed", "imported"}]
        skipped = [s for s in scans if s.get("status", "").lower() not in {"completed", "imported"}]

        for s in skipped:
            self.log(f"Skipping [{s['name']}] - status: {s.get('status', 'unknown')}")
            self.results["skipped"].append(s)

        self.log(f"-> {len(completed)} scans to download | {len(skipped)} skipped | workers: {self.max_workers}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(self.download_scan, s): s for s in completed}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    statuses = [v.get("status") if isinstance(v, dict) else v for v in result["formats"].values()]
                    has_error = any(s == "error" for s in statuses)
                    has_ok = any(s == "ok" for s in statuses)
                    if has_ok and not has_error:
                        self.results["success"].append(result)
                    else:
                        self.results["failed"].append(result)
                except Exception as e:
                    self.results["failed"].append({"error": str(e)})

        return self.results


# ── Flask Web UI ──────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder=None)
jobs = {}
jobs_lock = threading.Lock()


def make_job_id():
    return f"job_{int(time.time()*1000)}"


def run_download_job(job_id, config):
    logs = []
    def log(msg):
        ts = datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{ts}] {msg}")
        with jobs_lock:
            if job_id in jobs:
                jobs[job_id]["logs"] = logs[:]

    with jobs_lock:
        jobs[job_id]["status"] = "running"

    try:
        log("Connecting to Nessus...")
        client = NessusClient(
            host=config["host"], port=int(config.get("port", 8834)),
            username=config.get("username"), password=config.get("password"),
            access_key=config.get("access_key"), secret_key=config.get("secret_key"),
            verify_ssl=config.get("verify_ssl", False)
        )
        log("Connected successfully")

        downloader = BulkDownloader(
            client=client,
            output_dir=config.get("output_dir", "./nessus_downloads"),
            formats=config.get("formats", ["nessus", "html", "csv"]),
            max_workers=int(config.get("workers", 3)),
            log_callback=log
        )
        results = downloader.run(
            scan_ids=config.get("scan_ids") or None,
            folder_id=config.get("folder_id") or None
        )

        report_path = Path(config.get("output_dir", "./nessus_downloads")) / \
                      f"download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(results, indent=2))

        log(f"Done! Success: {len(results['success'])} | Failed: {len(results['failed'])} | Skipped: {len(results['skipped'])}")
        log(f"Report saved to: {report_path}")

        with jobs_lock:
            jobs[job_id].update({"status": "done", "results": results, "report_path": str(report_path)})
        client.logout()

    except Exception as e:
        log(f"Error: {e}")
        with jobs_lock:
            jobs[job_id].update({"status": "error", "error": str(e)})


@app.route("/")
def index():
    return EMBEDDED_HTML


@app.route("/api/test-connection", methods=["POST"])
def test_connection():
    data = request.json
    try:
        client = NessusClient(
            host=data["host"], port=int(data.get("port", 8834)),
            username=data.get("username"), password=data.get("password"),
            access_key=data.get("access_key"), secret_key=data.get("secret_key"),
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
        jobs[job_id] = {"id": job_id, "status": "pending", "logs": [], "results": None,
                        "started_at": datetime.now().isoformat()}
    threading.Thread(target=run_download_job, args=(job_id, config), daemon=True).start()
    return jsonify({"job_id": job_id})


@app.route("/api/job/<job_id>")
def get_job(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    return jsonify(job) if job else (jsonify({"error": "Not found"}), 404)


# ── Entry Point ───────────────────────────────────────────────────────────────
def launch_webui(port=5000):
    print(f"\n{'='*50}")
    print(f"  Nessus Bulk Downloader")
    print(f"  Open http://localhost:{port} in your browser")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*50}\n")
    threading.Timer(1.2, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    app.run(host="0.0.0.0", port=port, debug=False)


def launch_cli():
    import argparse
    parser = argparse.ArgumentParser(description="Nessus Bulk Downloader - CLI")
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=8834)
    parser.add_argument("--access-key")
    parser.add_argument("--secret-key")
    parser.add_argument("-u", "--username")
    parser.add_argument("-p", "--password")
    parser.add_argument("--formats", nargs="+", default=["nessus", "html", "csv"],
                        choices=["nessus", "html", "csv", "pdf", "db"])
    parser.add_argument("--scan-ids", nargs="+", type=int)
    parser.add_argument("--folder-id", type=int)
    parser.add_argument("--output-dir", default="./nessus_downloads")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--verify-ssl", action="store_true")
    args = parser.parse_args(sys.argv[2:])

    client = NessusClient(
        host=args.host, port=args.port,
        username=args.username, password=args.password,
        access_key=args.access_key, secret_key=args.secret_key,
        verify_ssl=args.verify_ssl
    )
    downloader = BulkDownloader(client, args.output_dir, args.formats, args.workers)
    results = downloader.run(scan_ids=args.scan_ids, folder_id=args.folder_id)
    print(f"\nDone! Success: {len(results['success'])} | Failed: {len(results['failed'])} | Skipped: {len(results['skipped'])}")
    client.logout()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        launch_cli()
    else:
        launch_webui()
