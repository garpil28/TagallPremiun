import json
import os
import sqlite3
import shutil
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.background import BackgroundScheduler

# ================= CONFIG =================
CONFIG_PATH = "config.json"
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError("❌ File config.json tidak ditemukan!")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

OWNER_ID = config["OWNER_ID"]
OWNER_USERNAME = config["OWNER_USERNAME"]
OWNER_NAME = config["OWNER_NAME"]
BOT_NAME = config["BOT_NAME"]
VERSION = config["VERSION"]
BOT_TOKEN = config["BOT_TOKEN"]
API_ID = config["API_ID"]
API_HASH = config["API_HASH"]

DB_PATH = "database.db"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

print(f"""
🚀 {BOT_NAME} v{VERSION} Aktif!
👑 Owner: {OWNER_NAME} (@{OWNER_USERNAME})
""")

# ========= DATABASE =========
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        active_until TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS bots (
        user_id INTEGER,
        token TEXT,
        partner_link TEXT,
        last_tag_date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )""")
    conn.commit()
    conn.close()

# ========= LOG =========
def log_action(text):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"log_{today}.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")

# ========= BACKUP =========
def backup_database():
    today = datetime.now().strftime("%Y%m%d")
    backup_file = os.path.join(LOG_DIR, f"backup_{today}")
    shutil.make_archive(backup_file, 'zip', '.', 'database.db')
    log_action("💾 Backup database otomatis.")

# ========= RESET TAGALL HARIAN =========
def reset_daily_tag_limit():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE bots SET last_tag_date=NULL")
    conn.commit()
    conn.close()
    log_action("♻️ Limit tagall harian direset.")

# ========= CEK USER PREMIUM =========
async def check_expiring_users(app):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, active_until FROM users")
    users = c.fetchall()
    conn.close()
    for uid, exp_date in users:
        if not exp_date:
            continue
        exp_date = datetime.strptime(exp_date, "%Y-%m-%d")
        days_left = (exp_date - datetime.now()).days
        if days_left == 2:
            try:
                await app.bot.send_message(
                    OWNER_ID,
                    f"⚠️ User `{uid}` masa aktif habis dalam 2 hari.",
                    parse_mode="Markdown"
                )
            except:
                pass

# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT active_until FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    if not user:
        await update.message.reply_text("❌ Kamu belum punya akses premium.\nHubungi admin untuk /addprem.")
        return
    active_until = datetime.strptime(user[0], "%Y-%m-%d")
    if active_until < datetime.now():
        await update.message.reply_text("⛔ Masa aktif kamu sudah habis. Hubungi admin untuk perpanjang.")
        return
    keyboard = [
        [InlineKeyboardButton("🔗 Set Link Partner", callback_data="set_partner")],
        [InlineKeyboardButton("🤖 Set Bot Token", callback_data="set_token")],
        [InlineKeyboardButton("🕓 Manual TagAll", callback_data="manual_tagall")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Selamat datang di *Auto TagAll Premium Bot v2.0*\n\nPilih menu:",
        reply_markup=reply_markup, parse_mode="Markdown"
    )

# ========= JALANKAN =========
if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    scheduler = BackgroundScheduler()
    scheduler.add_job(backup_database, "cron", hour=0, minute=5)
    scheduler.add_job(reset_daily_tag_limit, "cron", hour=0, minute=0)
    scheduler.add_job(lambda: check_expiring_users(app), "interval", hours=12)
    scheduler.start()

    log_action("🚀 Bot dimulai...")
    print("🤖 Auto TagAll Premium v2.0 aktif.")
    app.run_polling()
