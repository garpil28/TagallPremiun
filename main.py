import os
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
)
from apscheduler.schedulers.background import BackgroundScheduler
from config import OWNER_ID, OWNER_USERNAME, OWNER_NAME, BOT_NAME, VERSION, BOT_TOKEN, API_ID, API_HASH

# Folder logs dan database
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
DB_PATH = "database.db"

# ID grup logs
LOGS_CHAT_ID = -1003282574590

# ===== DATABASE INIT =====
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS partners (
        chat_id TEXT PRIMARY KEY,
        is_partner INTEGER DEFAULT 0,
        last_tag_date TEXT
    )""")
    conn.commit()
    conn.close()

# ===== LOG =====
def log_action(text):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"log_{today}.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")

# ===== KIRIM LOG KE GRUP =====
async def kirim_log(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    try:
        await context.bot.send_message(chat_id=LOGS_CHAT_ID, text=text)
    except Exception as e:
        log_action(f"❌ Gagal kirim log ke grup: {e}")

# ===== RESET HARIAN =====
def reset_daily():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE partners SET last_tag_date=NULL")
    conn.commit()
    conn.close()
    log_action("♻️ Reset limit tagall harian.")

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [
        [InlineKeyboardButton("🔗 Set Partner List", callback_data="set_partner")],
        [InlineKeyboardButton("🤖 Manual TagAll", callback_data="manual_tagall")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Selamat datang di *{BOT_NAME} v{VERSION}*\nOwner: {OWNER_NAME} (@{OWNER_USERNAME})",
        reply_markup=reply_markup, parse_mode="Markdown"
    )

# ===== CALLBACK BUTTON =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "set_partner":
        await query.edit_message_text("Kirim list chat_id/grup partner (satu per baris):")
        context.user_data["waiting_for"] = "partner_list"
    elif query.data == "manual_tagall":
        keyboard = [
            [InlineKeyboardButton("3m", callback_data="durasi_3"),
             InlineKeyboardButton("5m", callback_data="durasi_5")],
            [InlineKeyboardButton("20m", callback_data="durasi_20"),
             InlineKeyboardButton("30m", callback_data="durasi_30")],
            [InlineKeyboardButton("60m", callback_data="durasi_60"),
             InlineKeyboardButton("90m", callback_data="durasi_90")],
            [InlineKeyboardButton("♾️ Unlimited", callback_data="durasi_unlimit")]
        ]
        await query.edit_message_text("Pilih durasi TagAll manual:", reply_markup=InlineKeyboardMarkup(keyboard))

async def durasi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    durasi = query.data.replace("durasi_", "")
    await query.edit_message_text(f"⏱️ TagAll berjalan {durasi} menit otomatis.")
    log_action(f"Manual TagAll {durasi} menit dijalankan oleh {query.from_user.id}")
    await kirim_log(update, context, f"Manual TagAll {durasi} menit dijalankan oleh {query.from_user.username or query.from_user.id}")

# ===== PESAN =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    chat_id = update.message.chat_id

    # Partner list
    if context.user_data.get("waiting_for") == "partner_list":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        lines = text.splitlines()
        for chat in lines:
            c.execute(
                "INSERT OR REPLACE INTO partners(chat_id,is_partner,last_tag_date) VALUES(?,?,?)",
                (chat, 1, None)
            )
            log_action(f"Partner ditambahkan: {chat} oleh {user_id}")
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ Partner list berhasil disimpan ({len(lines)} grup).")
        context.user_data["waiting_for"] = None

    # Auto TagAll
    elif "/jalan" in text.lower() or text.lower() in ["tagall","pemerintah"]:
        keyboard = [
            [InlineKeyboardButton("3m", callback_data="durasi_3"),
             InlineKeyboardButton("5m", callback_data="durasi_5")],
            [InlineKeyboardButton("20m", callback_data="durasi_20"),
             InlineKeyboardButton("30m", callback_data="durasi_30")],
            [InlineKeyboardButton("60m", callback_data="durasi_60"),
             InlineKeyboardButton("90m", callback_data="durasi_90")],
            [InlineKeyboardButton("♾️ Unlimited", callback_data="durasi_unlimit")]
        ]
        await update.message.reply_text("Pilih durasi TagAll manual:", reply_markup=InlineKeyboardMarkup(keyboard))
        # Log ke grup logs
        await kirim_log(update, context, f"Manual TagAll diminta di chat {chat_id} oleh {update.effective_user.username or user_id}")

# ===== JALANKAN BOT =====
if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^(set_|manual)"))
    app.add_handler(CallbackQueryHandler(durasi_callback, pattern="^durasi_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(reset_daily, "cron", hour=0, minute=0)
    scheduler.start()

    log_action("🚀 Bot dimulai...")
    print(f"🤖 {BOT_NAME} v{VERSION} aktif.")
    app.run_polling()
