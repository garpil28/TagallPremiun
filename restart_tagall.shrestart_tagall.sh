#!/bin/bash
# =============================
# RESTART AUTO TAGALL BOT
# =============================

BOT_NAME="tagallbot"

# Masuk ke folder bot
cd "$(dirname "$0")"

# Aktifkan virtual environment
source venv/bin/activate

echo "📌 Menutup screen Auto TagAll lama jika ada..."
SCREENS=$(screen -ls | grep "$BOT_NAME" | awk '{print $1}')
if [ ! -z "$SCREENS" ]; then
    for PID in $SCREENS; do
        echo "⏹ Hentikan screen $PID..."
        kill -9 $PID
    done
fi

# Jalankan bot baru di screen
echo "🤖 Menjalankan bot baru di screen: $BOT_NAME"
screen -dmS "$BOT_NAME" bash -c "source venv/bin/activate && python3 main.py"

echo "✅ Bot Auto TagAll sudah berjalan di screen: $BOT_NAME"
echo "Gunakan 'screen -r $BOT_NAME' untuk melihat bot, Ctrl+A D untuk detach."
