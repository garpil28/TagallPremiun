import os
import sqlite3
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import OWNER_ID, OWNER_USERNAME, OWNER_NAME, BOT_NAME, VERSION, BOT_TOKEN, LOGS_CHAT_ID

# ===== FOLDER LOGS =====
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
DB_PATH = "database.db"

# ===== DATABASE =====
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS partners (
        chat_id TEXT PRIMARY KEY,
        name TEXT,
        date_added TEXT
    )""")
    conn.commit()
    conn.close()

def add_partner(chat_id, name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO partners VALUES (?, ?, ?)", (chat_id, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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

# ===== LOG SYSTEM =====
def log_action(text):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"log_{today}.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
    print(text)

# ===== TAGALL PROCESS =====
async def tagall(context, sender_id, mode="auto"):
    partners = get_partners()
    if not partners:
        return

    sender = await context.bot.get_chat(sender_id)
    name = sender.first_name
    start_time = datetime.now()

    log_action(f"🚀 TagAll ({mode}) dimulai oleh {name} (ID: {sender_id})")
    message = (
        f"🔔 *TagAll Dimulai*\n"
        f"👤 Pengguna: `{name}`\n"
        f"⚙️ Mode: `{mode}`\n"
        f"🕒 Waktu: {start_time.strftime('%H:%M:%S')}"
    )

    for target in [OWNER_ID, LOGS_CHAT_ID]:
        try:
            await context.bot.send_message(target, message, parse_mode="Markdown")
        except:
            pass

    for pid in partners:
        try:
            await context.bot.send_message(int(pid), f"🔔 TagAll dimulai oleh {name}")
            await asyncio.sleep(3)
        except Exception as e:
            log_action(f"⚠️ Gagal kirim ke {pid}: {e}")

    for i in range(5):
        await asyncio.sleep(60)
        for pid in partners:
            try:
                await context.bot.send_message(int(pid), f"⏳ TagAll berjalan {i+1}/5 menit...")
            except:
                pass

    for pid in partners:
        try:
            await context.bot.send_message(int(pid), "✅ TagAll berhenti otomatis setelah 5 menit.")
        except:
            pass

    log_action(f"✅ TagAll ({mode}) selesai oleh {name}")

    done_msg = (
        f"✅ *TagAll Selesai!*\n"
        f"👤 Pengguna: `{name}`\n"
        f"⚙️ Mode: `{mode}`\n"
        f"🕒 Durasi: 5 menit"
    )
    for target in [OWNER_ID, LOGS_CHAT_ID]:
        try:
            await context.bot.send_message(target, done_msg, parse_mode="Markdown")
        except:
            pass

    today_log = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
    if os.path.exists(today_log):
        await context.bot.send_document(LOGS_CHAT_ID, document=open(today_log, "rb"))

# ===== PERINTAH OWNER =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"🤖 *{BOT_NAME} v{VERSION}*\n"
        f"👑 Owner: {OWNER_NAME} (@{OWNER_USERNAME})\n\n"
        "Perintah:\n"
        "/addpartner <chat_id> <nama>\n"
        "/delpartner <chat_id>\n"
        "/listpartner\n"
        "/jalan – Jalankan manual TagAll"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def add_partner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Gunakan: /addpartner <chat_id> <nama>")
        return
    chat_id, name = context.args[0], " ".join(context.args[1:])
    add_partner(chat_id, name)
    await update.message.reply_text(f"✅ Partner {name} ({chat_id}) ditambahkan.")
    log_action(f"Partner {name} ({chat_id}) ditambahkan oleh Owner.")

async def del_partner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Gunakan: /delpartner <chat_id>")
        return
    chat_id = context.args[0]
    remove_partner(chat_id)
    await update.message.reply_text(f"🗑️ Partner {chat_id} dihapus.")
    log_action(f"Partner {chat_id} dihapus oleh Owner.")

async def list_partner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    partners = get_partners()
    if not partners:
        await update.message.reply_text("Belum ada partner terdaftar.")
        return
    await update.message.reply_text("📋 List Partner:\n" + "\n".join(partners))

async def jalan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tagall(context, update.effective_user.id, mode="manual")

async def detect_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "t.me/" in update.message.text:
        await tagall(context, update.effective_user.id, mode="auto")

# ===== MAIN =====
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addpartner", add_partner_cmd))
    app.add_handler(CommandHandler("delpartner", del_partner_cmd))
    app.add_handler(CommandHandler("listpartner", list_partner_cmd))
    app.add_handler(CommandHandler("jalan", jalan_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, detect_link))

    print(f"🤖 {BOT_NAME} v{VERSION} aktif.")
    log_action("Bot dijalankan.")
    app.run_polling()

if __name__ == "__main__":
    main()
