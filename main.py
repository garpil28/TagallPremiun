import os
import sqlite3
import shutil
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from apscheduler.schedulers.background import BackgroundScheduler
from config import OWNER_USERNAME, OWNER_NAME, BOT_NAME, VERSION

# === KONFIGURASI DASAR ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
DB_PATH = "database.db"
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

if not BOT_TOKEN or OWNER_ID == 0:
    raise ValueError("❌ BOT_TOKEN atau OWNER_ID belum diatur di VPS.\nGunakan: export BOT_TOKEN='xxx' dan export OWNER_ID='xxx'")

# === INISIALISASI DATABASE ===
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

# === LOGGING AKTIVITAS ===
def log_action(text):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"log_{today}.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")

# === BACKUP OTOMATIS DATABASE ===
def backup_database():
    today = datetime.now().strftime("%Y%m%d")
    backup_file = os.path.join(LOG_DIR, f"backup_{today}")
    shutil.make_archive(backup_file, 'zip', '.', 'database.db')
    log_action("💾 Backup otomatis database dibuat.")

# === RESET LIMIT TAGALL HARIAN ===
def reset_daily_tag_limit():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE bots SET last_tag_date=NULL")
    conn.commit()
    conn.close()
    log_action("♻️ Limit tagall harian direset otomatis.")

# === CEK MASA AKTIF USER & NOTIFIKASI KE OWNER ===
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
                    OWNER_ID, f"⚠️ User `{uid}` masa aktifnya akan habis dalam 2 hari.",
                    parse_mode="Markdown"
                )
            except:
                pass

# === MENU START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT active_until FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()

    if user is None:
        await update.message.reply_text(f"❌ Kamu belum punya akses premium.\nHubungi @{OWNER_USERNAME} untuk /addprem.")
        return

    active_until = datetime.strptime(user[0], "%Y-%m-%d")
    if active_until < datetime.now():
        await update.message.reply_text("⛔ Masa aktif kamu sudah habis. Hubungi admin untuk perpanjang.")
        return

    keyboard = [
        [InlineKeyboardButton("🔗 Set Link Partner", callback_data="set_partner")],
        [InlineKeyboardButton("🤖 Set Bot Token", callback_data="set_token")],
        [InlineKeyboardButton("🕓 Manual TagAll", callback_data="manual_tagall")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Selamat datang di *{BOT_NAME} v{VERSION}*\n"
        f"Owner: @{OWNER_USERNAME}\n"
        "Gunakan menu di bawah:",
        reply_markup=reply_markup, parse_mode="Markdown"
    )

# === TAMBAH AKSES PREMIUM ===
async def addprem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Hanya owner yang bisa pakai perintah ini.")

    if not context.args:
        return await update.message.reply_text("Gunakan format: `/addprem <user_id>`", parse_mode="Markdown")

    target_id = int(context.args[0])
    active_until = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, active_until) VALUES (?, ?)", (target_id, active_until))
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Akses premium diberikan ke user `{target_id}` hingga {active_until}",
        parse_mode="Markdown"
    )
    try:
        await context.bot.send_message(
            target_id,
            f"🎉 Akses premium kamu telah diaktifkan hingga *{active_until}*.\nGunakan /start untuk mengatur botmu!",
            parse_mode="Markdown"
        )
    except:
        pass
    log_action(f"Owner menambah premium untuk user {target_id} hingga {active_until}")

# === CALLBACK BUTTON ===
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT active_until FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()

    if not user or datetime.strptime(user[0], "%Y-%m-%d") < datetime.now():
        return await query.edit_message_text("❌ Masa aktif kamu sudah habis.")

    if query.data == "set_partner":
        await query.edit_message_text("Kirim link grup partner kamu:")
        context.user_data["waiting_for"] = "partner"
    elif query.data == "set_token":
        await query.edit_message_text("Kirim token bot kamu:")
        context.user_data["waiting_for"] = "token"
    elif query.data == "manual_tagall":
        keyboard = [
            [InlineKeyboardButton("3m", callback_data="durasi_3"),
             InlineKeyboardButton("5m", callback_data="durasi_5"),
             InlineKeyboardButton("20m", callback_data="durasi_20")],
            [InlineKeyboardButton("40m", callback_data="durasi_40"),
             InlineKeyboardButton("90m", callback_data="durasi_90"),
             InlineKeyboardButton("♾️ Unlimited", callback_data="durasi_unlimit")]
        ]
        await query.edit_message_text("Pilih durasi TagAll:", reply_markup=InlineKeyboardMarkup(keyboard))

async def durasi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    durasi = query.data.replace("durasi_", "")
    await query.edit_message_text(f"⏱️ Durasi TagAll: {durasi} menit.\nTagAll akan berjalan otomatis...")
    log_action(f"User {query.from_user.id} mulai tagall manual ({durasi} menit)")

# === PESAN DARI USER ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if context.user_data.get("waiting_for") == "partner":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO bots (user_id, partner_link, last_tag_date, token)
            VALUES (?, ?, ?, (SELECT token FROM bots WHERE user_id=?))
        """, (user_id, text, None, user_id))
        conn.commit()
        conn.close()
        await update.message.reply_text("✅ Link partner berhasil disimpan.")
        context.user_data["waiting_for"] = None
        log_action(f"User {user_id} set partner: {text}")

    elif context.user_data.get("waiting_for") == "token":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO bots (user_id, token, last_tag_date, partner_link)
            VALUES (?, ?, ?, (SELECT partner_link FROM bots WHERE user_id=?))
        """, (user_id, text, None, user_id))
        conn.commit()
        conn.close()
        await update.message.reply_text("✅ Token bot berhasil disimpan.")
        context.user_data["waiting_for"] = None
        log_action(f"User {user_id} set token bot.")

    elif text.lower() in ["pemerintah", "/tagall"]:
        keyboard = [
            [InlineKeyboardButton("3m", callback_data="durasi_3"),
             InlineKeyboardButton("5m", callback_data="durasi_5"),
             InlineKeyboardButton("20m", callback_data="durasi_20")],
            [InlineKeyboardButton("40m", callback_data="durasi_40"),
             InlineKeyboardButton("90m", callback_data="durasi_90"),
             InlineKeyboardButton("♾️ Unlimited", callback_data="durasi_unlimit")]
        ]
        await update.message.reply_text("Pilih durasi manual TagAll:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text.lower() in ["/cancel", "cancel"]:
        await update.message.reply_text("🛑 TagAll dibatalkan oleh user.")
        log_action(f"User {user_id} membatalkan TagAll.")

# === JALANKAN BOT ===
if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addprem", addprem))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^(set_|manual)"))
    app.add_handler(CallbackQueryHandler(durasi_callback, pattern="^durasi_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    scheduler = BackgroundScheduler()
    scheduler.add_job(backup_database, "cron", hour=0, minute=5)
    scheduler.add_job(reset_daily_tag_limit, "cron", hour=0, minute=0)
    scheduler.add_job(lambda: check_expiring_users(app), "interval", hours=12)
    scheduler.start()

    log_action("🚀 Bot dimulai...")
    print(f"🤖 {BOT_NAME} v{VERSION} aktif.")
    app.run_polling()
