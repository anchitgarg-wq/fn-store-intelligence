"""
Steve Madden Store Intelligence — Chunk B web service.

Flow:
  Zapier (gate passed) --POST /refresh--> this service
     body JSON: { "inventory_url": ..., "sales_url": ..., "kpi_url": ...,
                  "key_master_url": ..., "image_master_url": ...,
                  "as_of": "YYYY-MM-DD" (optional), "token": "<shared secret>" }
  -> download the 5 files into a temp folder under the EXACT names aggregate_core.py expects
  -> run aggregate_core.py (unchanged business logic) to produce summary.json
  -> wrap as payload.js  (window.DASHBOARD_DATA = {...};)
  -> store it; serve at GET /payload.js  (CORS-open, for Shopify)

Design notes:
- The aggregation script is run unchanged via subprocess; we only rename inputs to the
  names it already globs for. This keeps the proven logic untouched.
- Image master: the old pipeline used Image_URL_s_Part_1/2/3 + Link_Update. The new single
  Image_Master.xlsx is written as BOTH Image_URL_s_Part_2.xlsx (Key/Image) and, if its columns
  differ, normalised first. See save_image_master().
- If any required file is missing/unreadable, we DO NOT overwrite the last good payload.js.
"""
import os, sys, json, tempfile, shutil, subprocess, traceback, datetime as dt
import requests
import pandas as pd
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# ---- config ----
SHARED_TOKEN = os.environ.get("REFRESH_TOKEN", "")  # set in Render env; Zapier sends same value
# Persisted output. Render's disk is ephemeral across deploys but stable while running;
# for durability across restarts, attach a Render Disk mounted at /data and set PAYLOAD_DIR=/data.
PAYLOAD_DIR = os.environ.get("PAYLOAD_DIR", os.path.dirname(os.path.abspath(__file__)))
PAYLOAD_PATH = os.path.join(PAYLOAD_DIR, "payload.js")
STATUS_PATH = os.path.join(PAYLOAD_DIR, "last_status.json")

# Map incoming URL keys -> exact filenames aggregate_core_fn.py expects in its input folder.
TARGET_NAMES = {
    "inventory_url":   "Inventory_FN.xlsx",
    "sales_url":       "Yest_Sales_FN.xlsx",
    "kpi_url":         "04__Store_KPI__For_Live_Dashboard_-_Anchit_.xlsx",
    "key_master_url":  "FN_Color_Code_Master.xlsx",
    # image master handled specially (see save_image_master)
}


def _extract_drive_id(url):
    """Pull the Drive file id out of a uc?id=... or /d/<id>/ style URL."""
    import re
    m = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return m.group(1)
    return None


def _looks_like_html(first_bytes):
    head = first_bytes[:512].lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"<title>google drive" in head


def _download(url, dest_path):
    """Download a file, transparently handling Google Drive's large-file
    'can't scan for viruses' interstitial. Validates the result is a real
    XLSX (zip signature 'PK') so we never hand pandas an HTML page."""
    session = requests.Session()
    # Prefer the Drive API media endpoint when we can identify the id — it
    # returns bytes directly without the interstitial.
    file_id = _extract_drive_id(url)
    candidates = []
    if file_id:
        candidates.append(f"https://drive.google.com/uc?export=download&id={file_id}")
    candidates.append(url)

    last_err = None
    for base in candidates:
        try:
            r = session.get(base, timeout=300, stream=True)
            r.raise_for_status()
            # Peek at the first chunk to see if it's the HTML interstitial.
            it = r.iter_content(chunk_size=1 << 20)
            first = next(it, b"")
            if _looks_like_html(first) and file_id:
                # Find the confirm token (newer Drive uses a form/confirm param).
                import re
                body = first + b"".join(it)
                token = None
                m = re.search(rb"confirm=([0-9A-Za-z_\-]+)", body)
                if m:
                    token = m.group(1).decode()
                # Newer interstitial posts to drive.usercontent.google.com
                confirm_url = (f"https://drive.usercontent.google.com/download?"
                               f"id={file_id}&export=download&confirm={token or 't'}")
                r2 = session.get(confirm_url, timeout=300, stream=True)
                r2.raise_for_status()
                it2 = r2.iter_content(chunk_size=1 << 20)
                first2 = next(it2, b"")
                if _looks_like_html(first2):
                    last_err = ValueError("still got HTML after confirm token")
                    continue
                with open(dest_path, "wb") as f:
                    if first2:
                        f.write(first2)
                    for chunk in it2:
                        if chunk:
                            f.write(chunk)
            else:
                with open(dest_path, "wb") as f:
                    if first:
                        f.write(first)
                    for chunk in it:
                        if chunk:
                            f.write(chunk)

            # Validate: non-empty and looks like a real xlsx (zip = 'PK\x03\x04').
            if os.path.getsize(dest_path) == 0:
                last_err = ValueError(f"downloaded file is empty: {dest_path}")
                continue
            with open(dest_path, "rb") as f:
                sig = f.read(4)
            if sig[:2] != b"PK":
                last_err = ValueError(
                    f"downloaded content is not a valid .xlsx (got signature {sig!r}). "
                    f"Likely a Google Drive permission/interstitial page. "
                    f"Ensure the file is shared so the link returns bytes.")
                continue
            return  # success
        except Exception as e:
            last_err = e
            continue
    raise last_err or ValueError(f"failed to download {url}")


def save_image_master(url, folder):
    """Download the FN image master and save it under the name the FN aggregate reads
    directly (FN_Image_Master.xlsx). The FN script auto-detects the color-code and link
    columns, so no Part_1/2/3 normalisation is needed."""
    _download(url, os.path.join(folder, "FN_Image_Master.xlsx"))


def run_refresh(payload):
    work = tempfile.mkdtemp(prefix="smrefresh_")
    folder = os.path.join(work, "inputs") + os.sep
    os.makedirs(folder, exist_ok=True)
    try:
        # 1) download the four straightforward files
        for key, fname in TARGET_NAMES.items():
            url = payload.get(key)
            if not url:
                raise ValueError(f"missing required url: {key}")
            _download(url, os.path.join(folder, fname))
        # 2) image master (normalised)
        if not payload.get("image_master_url"):
            raise ValueError("missing required url: image_master_url")
        save_image_master(payload["image_master_url"], folder)

        # 3) run the unchanged aggregation
        out_json = os.path.join(work, "summary.json")
        env = dict(os.environ)
        as_of = payload.get("as_of")
        if as_of:
            env["AS_OF_DATE"] = as_of  # else aggregate defaults to today-1
        proc = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "aggregate_core_fn.py"), folder, out_json],
            capture_output=True, text=True, env=env, timeout=600)
        if proc.returncode != 0:
            raise RuntimeError(f"aggregate failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")

        # 4) wrap summary.json -> payload.js, write ATOMICALLY so we never serve a half file
        with open(out_json, "r") as f:
            data = f.read()
        os.makedirs(PAYLOAD_DIR, exist_ok=True)
        tmp_payload = PAYLOAD_PATH + ".tmp"
        with open(tmp_payload, "w") as f:
            f.write("window.DASHBOARD_DATA = " + data + ";")
        os.replace(tmp_payload, PAYLOAD_PATH)  # atomic swap; previous good file replaced only on success

        status = {"ok": True, "at": dt.datetime.utcnow().isoformat() + "Z",
                  "as_of": as_of or "(default today-1)",
                  "bytes": os.path.getsize(PAYLOAD_PATH),
                  "agg_stdout_tail": proc.stdout.strip().splitlines()[-3:]}
        with open(STATUS_PATH, "w") as f:
            json.dump(status, f)
        return status
    finally:
        shutil.rmtree(work, ignore_errors=True)


@app.route("/refresh", methods=["POST"])
def refresh():
    body = request.get_json(force=True, silent=True) or {}
    if SHARED_TOKEN and body.get("token") != SHARED_TOKEN:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    # Mark a run as started so /status reflects in-progress state.
    try:
        with open(STATUS_PATH, "w") as f:
            json.dump({"ok": None, "state": "running",
                       "at": dt.datetime.utcnow().isoformat() + "Z"}, f)
    except Exception:
        pass

    # Do the heavy work in a background thread and return immediately,
    # so Zapier's webhook gets a fast 200 instead of timing out (~30s limit).
    def _worker(payload):
        try:
            run_refresh(payload)
        except Exception as e:
            err = {"ok": False, "at": dt.datetime.utcnow().isoformat() + "Z",
                   "error": str(e), "trace": traceback.format_exc()[-1500:]}
            try:
                with open(STATUS_PATH, "w") as f:
                    json.dump(err, f)
            except Exception:
                pass
            # last good payload.js is left untouched on failure.

    import threading
    threading.Thread(target=_worker, args=(body,), daemon=True).start()
    return jsonify({"ok": True, "state": "accepted",
                    "message": "refresh started; check /status for result"}), 202


@app.route("/payload.js", methods=["GET"])
def payload_js():
    if not os.path.exists(PAYLOAD_PATH):
        return Response("/* no payload generated yet */", mimetype="application/javascript",
                        headers={"Access-Control-Allow-Origin": "*"})
    with open(PAYLOAD_PATH, "r") as f:
        body = f.read()
    return Response(body, mimetype="application/javascript",
                    headers={"Access-Control-Allow-Origin": "*",
                             # Explicitly non-cacheable: the payload is regenerated on every
                             # refresh, so any cached copy is stale. The previous
                             # "no-cache, max-age=60" was contradictory and let CDNs/browsers
                             # serve an old payload for up to a minute (or longer in practice).
                             "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                             "Pragma": "no-cache",
                             "Expires": "0"})


@app.route("/status", methods=["GET"])
def status():
    if os.path.exists(STATUS_PATH):
        with open(STATUS_PATH) as f:
            return Response(f.read(), mimetype="application/json",
                            headers={"Access-Control-Allow-Origin": "*"})
    return jsonify({"ok": None, "msg": "no run yet"})


@app.route("/", methods=["GET"])
def health():
    return jsonify({"service": "sm-store-intelligence", "ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
