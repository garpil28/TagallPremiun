import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import OWNER_ID, OWNER_USERNAME, OWNER_NAME, BOT_NAME, VERSION, BOT_TOKEN, API_ID, API_HASH

# Folder logs
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
DB_PATH = "database.db"

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
    keyboard = [
        [InlineKeyboardButton("🔗 Set Partner List", callback_data="set_partner")],
        [InlineKeyboardButton("🤖 Manual TagAll", callback_data="manual_tagall")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Selamat datang di *{BOT_NAME} v{VERSION}*\nOwner: {OWNER_NAME} (@{OWNER_USERNAME})",
        reply_markup=reply_markup,
        parse_mode="Markdown"
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

# ===== HANDLE MESSAGE =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    # Input partner list
    if context.user_data.get("waiting_for") == "partner_list":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        lines = text.splitlines()
        for chat_id in lines:
            c.execute("INSERT OR REPLACE INTO partners(chat_id,is_partner,last_tag_date) VALUES(?,?,?)", (chat_id,1,None))
            log_action(f"Partner ditambahkan: {chat_id} oleh {user_id}")
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ Partner list berhasil disimpan ({len(lines)} grup).")
        context.user_data["waiting_for"] = None
        return

    # Auto TagAll partner / manual
    if any(x in text.lower() for x in ["tagall","pemerintah","/jalan"]):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Cek apakah grup partner
        chat_id = str(update.effective_chat.id)
        c.execute("SELECT is_partner,last_tag_date FROM partners WHERE chat_id=?", (chat_id,))
        row = c.fetchone()
        durasi = 2  # default 2 menit
        if row and row[0] == 1:
            # Partner -> 5 menit
            durasi = 5
            last_tag = row[1]
            today = datetime.now().strftime("%Y-%m-%d")
            if last_tag == today:
                await update.message.reply_text("⚠️ TagAll partner hanya 1x per hari.")
                return
            # Update last_tag_date
            c.execute("UPDATE partners SET last_tag_date=? WHERE chat_id=?", (today, chat_id))
            conn.commit()
        conn.close()
        await update.message.reply_text(f"🤖 TagAll dimulai otomatis selama {durasi} menit...")
        log_action(f"Auto TagAll dijalankan oleh {user_id} di chat {chat_id} ({'partner' if durasi==5 else 'non-partner'})")

        # Simulasi tagall delay (replace dengan logika tagall asli jika mau)
        await asyncio.sleep(durasi*60)
        await update.message.reply_text(f"✅ TagAll selesai ({durasi} menit).")
        log_action(f"Auto TagAll selesai di chat {chat_id}")

# ===== RUN BOT =====
if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^(set_|manual)"))
    app.add_handler(CallbackQueryHandler(durasi_callback, pattern="^durasi_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(reset_daily, "cron", hour=0, minute=0)  # Reset harian
    scheduler.start()

    log_action("🚀 Bot dimulai...")
    print(f"🤖 {BOT_NAME} v{VERSION} aktif.")
    app.run_polling()
