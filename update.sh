#!/bin/bash
echo "🚀 Updating bot from GitHub..."

# Stop bot yang sedang jalan
pkill -f main.py 2>/dev/null

# Pull update terbaru dari GitHub
git pull origin main

# Pastikan virtualenv aktif
source ~/belajar/venv/bin/activate

# Jalankan ulang bot
nohup python3 main.py > logs/update_$(date +"%Y%m%d_%H%M%S").log 2>&1 &

echo "✅ Bot updated & restarted successfully!"
