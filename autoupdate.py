import os
import requests
import time
import subprocess
from datetime import datetime
from config import OWNER_ID, BOT_NAME

# ===== CONFIG REPO =====
GITHUB_RAW_URL = "https://raw.githubusercontent.com/USERNAME/REPO/main/main.py"  # Ganti sesuai repo kamu
LOCAL_FILE = "main.py"
CHECK_INTERVAL = 300  # 300 detik = 5 menit

def get_remote_code():
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=10)
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(f"[Updater] Gagal cek update: {e}")
        return None

def get_local_code():
    if not os.path.exists(LOCAL_FILE):
        return ""
    with open(LOCAL_FILE, "r", encoding="utf-8") as f:
        return f.read()

def restart_bot():
    print("[Updater] Restarting bot...")
    subprocess.Popen(["python3", "main.py"])
    os._exit(0)

def auto_update_loop():
    print(f"[Updater] {BOT_NAME} auto-updater aktif.")
    while True:
        remote = get_remote_code()
        local = get_local_code()
        if remote and remote.strip() != local.strip():
            print(f"[Updater] 🚀 Update baru ditemukan pada {datetime.now()}")
            with open(LOCAL_FILE, "w", encoding="utf-8") as f:
                f.write(remote)
            restart_bot()
        time.sleep(CHECK_INTERVAL)
