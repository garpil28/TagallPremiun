#!/bin/bash
echo "🚀 Starting TagallPremiun super proper bot maintenance..."

# === 1️⃣ Folder project ===
PROJECT_DIR=~/belajar
cd "$PROJECT_DIR" || { echo "❌ Folder project tidak ditemukan!"; exit 1; }

# === 2️⃣ Virtualenv ===
VENV_PATH="$PROJECT_DIR/venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH" || { echo "❌ Gagal aktifkan virtualenv!"; exit 1; }
else
    echo "❌ Virtualenv tidak ditemukan di $VENV_PATH"
    exit 1
fi

# === 3️⃣ Cek apakah bot lama berjalan ===
SCREEN_NAME="TagallPremiunBot"
BOT_PID=$(pgrep -f "python3 main.py")

if screen -list | grep -q "$SCREEN_NAME"; then
    echo "🛑 Bot lama sedang berjalan di screen ($SCREEN_NAME), menghentikan..."
    screen -S "$SCREEN_NAME" -X quit
    sleep 2
elif [ ! -z "$BOT_PID" ]; then
    echo "🛑 Bot lama sedang berjalan (PID: $BOT_PID), menghentikan..."
    kill "$BOT_PID"
    sleep 2
else
    echo "ℹ️ Tidak ada bot lama yang berjalan."
fi

# === 4️⃣ Backup logs lama ===
LOG_DIR="$PROJECT_DIR/logs"
if [ -d "$LOG_DIR" ] && [ "$(ls -A $LOG_DIR)" ]; then
    BACKUP_DIR="$PROJECT_DIR/logs_backup_$(date +"%Y%m%d_%H%M%S")"
    mkdir -p "$BACKUP_DIR"
    mv "$LOG_DIR"/* "$BACKUP_DIR"/
    echo "💾 Backup logs lama dibuat di $BACKUP_DIR"
fi
mkdir -p "$LOG_DIR"

# === 5️⃣ Pull update GitHub TagallPremiun ===
git pull https://github.com/garpil28/TagallPremiun.git main || { echo "❌ Git pull gagal!"; exit 1; }
echo "✅ Update GitHub berhasil."

# === 6️⃣ Jalankan bot di background dengan screen ===
screen -dmS "$SCREEN_NAME" bash -c "python3 main.py > $LOG_DIR/bot_$(date +"%Y%m%d_%H%M%S").log 2>&1"
echo "🚀 Bot dijalankan di background dengan screen session: $SCREEN_NAME"

# === 7️⃣ Monitoring sederhana (jika bot crash, auto restart) ===
(
while true; do
    sleep 60
    BOT_PID_CHECK=$(pgrep -f "python3 main.py")
    if [ -z "$BOT_PID_CHECK" ]; then
        echo "⚠️ Bot tidak berjalan, restarting..."
        screen -dmS "$SCREEN_NAME" bash -c "python3 main.py > $LOG_DIR/bot_$(date +"%Y%m%d_%H%M%S").log 2>&1"
        echo "✅ Bot di-restart otomatis."
    fi
done
) &
echo "✅ Super proper maintenance script selesai. Bot siap berjalan."
