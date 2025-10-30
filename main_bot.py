import os
import sqlite3
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from config import OWNER_IDS, OWNER_USERNAME, OWNER_NAME, BOT_NAME, VERSION, BOT_TOKEN, LOG_GROUP_ID

# ===== FOLDER LOGS =====
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
DB_PATH = "database.db"

# ===== DATABASE =====
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS partners (
            chat_id TEXT PRIMARY KEY,
            name TEXT,
            date_added TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS running_sessions (
            chat_id TEXT PRIMARY KEY,
            end_time TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_partner(chat_id, name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO partners VALUES (?, ?, ?)",
              (chat_id, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def remove_partner(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM partners WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

def get_partners():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT chat_id FROM partners")
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows

def is_running(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT end_time FROM running_sessions WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()
    if row:
        end_time = datetime.fromisoformat(row[0])
        return datetime.now() < end_time
    return False

def start_session(chat_id, duration_min):
    end_time = datetime.now() + timedelta(minutes=duration_min)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO running_sessions VALUES (?, ?)",
              (chat_id, end_time.isoformat()))
    conn.commit()
    conn.close()

def end_session(chat_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM running_sessions WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

# ===== LOG SYSTEM =====
def log_action(text):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"log_{today}.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
    print(text)

# ===== TAGALL PROCESS =====
async def tagall(context, chat_id, sender_name, duration_min=5, mode="auto"):
    if is_running(chat_id):
        await context.bot.send_message(chat_id, "⚠️ TagAll sedang berjalan, tunggu hingga selesai.")
        return

    partners = get_partners()
    is_partner = str(chat_id) in partners
    duration = duration_min if is_partner else 2

    start_session(chat_id, duration)
    log_action(f"🚀 TagAll ({mode}) dimulai oleh {sender_name} di chat {chat_id} selama {duration} menit.")

    # Ambil member grup untuk di-tag
    try:
        chat = await context.bot.get_chat(chat_id)
        members = await chat.get_members()
    except Exception as e:
        members = []
        log_action(f"⚠️ Gagal ambil member chat {chat_id}: {e}")

    for i in range(duration):
        if not is_running(chat_id):
            break
        text = f"⏰ TagAll berjalan {i+1}/{duration} menit oleh {sender_name}\n\n"
        mention_list = []
        for m in members:
            if m.user.is_bot:
                continue
            mention_list.append(f"[{m.user.first_name}](tg://user?id={m.user.id})")
        text += " ".join(mention_list) if mention_list else "Belum ada member"
        await context.bot.send_message(chat_id, text, parse_mode="Markdown")
        await asyncio.sleep(60)

    await context.bot.send_message(chat_id, f"✅ TagAll berhenti otomatis setelah {duration} menit.")
    end_session(chat_id)
    log_action(f"✅ TagAll ({mode}) selesai oleh {sender_name} di chat {chat_id}")

# ===== BUTTON HANDLER /JALAN =====
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    duration = int(query.data.split("_")[1])
    sender_name = query.from_user.first_name
    await query.edit_message_text(f"▶️ TagAll dimulai selama {duration} menit oleh {sender_name}...")
    await tagall(context, query.message.chat_id, sender_name, duration_min=duration, mode="manual")

# ===== PERINTAH =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"🤖 *{BOT_NAME} v{VERSION}*\n"
        f"👑 Owner: {OWNER_NAME} (@{OWNER_USERNAME})\n\n"
        "Perintah owner:\n"
        "/addpartner <chat_id> <nama>\n"
        "/delpartner <chat_id>\n"
        "/listpartner\n\n"
        "Perintah grup:\n"
        "/jalan – Jalankan TagAll manual."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def add_partner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Gunakan: /addpartner <chat_id> <nama>")
        return
    chat_id, name = context.args[0], " ".join(context.args[1:])
    add_partner(chat_id, name)
    await update.message.reply_text(f"✅ Partner {name} ({chat_id}) ditambahkan.")
    log_action(f"Partner {name} ({chat_id}) ditambahkan oleh Owner.")

async def del_partner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        return
    if not context.args:
        await update.message.reply_text("Gunakan: /delpartner <chat_id>")
        return
    chat_id = context.args[0]
    remove_partner(chat_id)
    await update.message.reply_text(f"🗑️ Partner {chat_id} dihapus.")
    log_action(f"Partner {chat_id} dihapus oleh Owner.")

async def list_partner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        return
    partners = get_partners()
    if not partners:
        await update.message.reply_text("Belum ada partner terdaftar.")
        return
    await update.message.reply_text("📋 List Partner:\n" + "\n".join(partners))

# ===== TAGALL MANUAL DI GRUP =====
async def jalan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("3m", callback_data="durasi_3"),
         InlineKeyboardButton("5m", callback_data="durasi_5"),
         InlineKeyboardButton("10m", callback_data="durasi_10")],
        [InlineKeyboardButton("20m", callback_data="durasi_20"),
         InlineKeyboardButton("30m", callback_data="durasi_30")]
    ]
    await update.message.reply_text("Pilih durasi TagAll:", reply_markup=InlineKeyboardMarkup(keyboard))

# ===== DETEKSI OTOMATIS =====
async def detect_auto_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "t.me/" in update.message.text.lower():
        sender_name = update.effective_user.first_name
        chat_id = update.effective_chat.id
        await tagall(context, chat_id, sender_name, mode="auto")

# ===== MAIN =====
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addpartner", add_partner_cmd))
    app.add_handler(CommandHandler("delpartner", del_patner_cmd))
    app.add_handler(CommandHandler("listpartner", list_partner_cmd))
    app.add_handler(CommandHandler("jalan", jalan_cmd))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^durasi_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, detect_auto_tag))

    print(f"🤖 {BOT_NAME} v{VERSION} aktif.")
    log_action("Bot dijalankan.")
    app.run_polling()

if __name__ == "__main__":
    main()
