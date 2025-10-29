import os
import sqlite3
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from apscheduler.schedulers.background import BackgroundScheduler
from config import OWNER_ID, OWNER_USERNAME, OWNER_NAME, BOT_NAME, VERSION, BOT_TOKEN

# ========== CONFIG ==========
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
DB_PATH = "database.db"
LOGS_CHAT_ID = -1003282574590  # ID grup logs kamu

# ========== INIT DATABASE ==========
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

# ========== LOGGING ==========
def log_action(text):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"log_{today}.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")

# ========== RESET HARIAN ==========
def reset_daily():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE partners SET last_tag_date=NULL")
    conn.commit()
    conn.close()
    log_action("♻️ Reset harian selesai.")

# ========== START COMMAND ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        keyboard = [
            [InlineKeyboardButton("📝 Edit Partner List", callback_data="set_partner")],
            [InlineKeyboardButton("📄 Lihat Partner List", callback_data="lihat_partner")]
        ]
        await update.message.reply_text(
            f"👋 Hai *{OWNER_NAME}*\nBot *{BOT_NAME} v{VERSION}* aktif!\n\nGunakan tombol di bawah untuk mengatur grup partner.",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "🤖 Bot aktif!\nKirim pesan berisi link grup untuk mulai TagAll otomatis selama 5 menit."
        )

# ========== CALLBACK HANDLER ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id != OWNER_ID:
        await query.edit_message_text("❌ Hanya owner yang bisa mengatur partner.")
        return

    if query.data == "set_partner":
        await query.edit_message_text("📝 Kirim daftar *chat_id grup partner* (satu per baris):", parse_mode="Markdown")
        context.user_data["waiting_for"] = "partner_list"

    elif query.data == "lihat_partner":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT chat_id FROM partners WHERE is_partner=1")
        rows = c.fetchall()
        conn.close()
        if rows:
            daftar = "\n".join([r[0] for r in rows])
            await query.edit_message_text(f"📋 Grup partner terdaftar:\n\n{daftar}")
        else:
            await query.edit_message_text("📭 Belum ada partner terdaftar.")

# ========== TAGALL PROSES ==========
async def tagall_process(context, source, partners, mode="auto"):
    user_info = None
    try:
        user_info = await context.bot.get_chat(source)
        source_name = f"{user_info.first_name} (ID: {source})"
    except:
        source_name = str(source)

    log_action(f"🚀 TagAll ({mode}) dimulai oleh {source_name}")
    start_time = datetime.now()

    # 🔔 Kirim notifikasi ke OWNER
    try:
        await context.bot.send_message(
            OWNER_ID,
            f"🔔 *TagAll dimulai!*\n\n👤 Pengguna: `{source_name}`\n⚙️ Mode: `{mode}`\n🕒 Waktu: {start_time.strftime('%H:%M:%S')}",
            parse_mode="Markdown"
        )
    except:
        pass

    # Kirim pesan ke tiap grup partner
    for pid in partners:
        try:
            await context.bot.send_message(int(pid), f"🔔 TagAll {mode} dimulai oleh {source_name}")
            await asyncio.sleep(3)  # delay 3 detik biar aman
        except Exception as e:
            log_action(f"⚠️ Gagal kirim ke {pid}: {e}")

    # Jalan selama 5 menit
    for minute in range(1, 6):
        await asyncio.sleep(60)
        elapsed = (datetime.now() - start_time).seconds
        for pid in partners:
            try:
                await context.bot.send_message(int(pid), f"⏳ TagAll berjalan {minute}/5 menit...")
            except:
                pass
        if elapsed >= 300:
            break

    # Selesai
    for pid in partners:
        try:
            await context.bot.send_message(int(pid), "✅ TagAll berhenti otomatis setelah 5 menit.")
        except:
            pass

    # 🔔 Kirim laporan ke grup logs
    await context.bot.send_message(LOGS_CHAT_ID, f"📁 TagAll selesai dijalankan oleh {source_name}")

    today_log = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
    if os.path.exists(today_log):
        await context.bot.send_document(LOGS_CHAT_ID, document=open(today_log, "rb"))

    # 🔔 Kirim laporan ke OWNER
    try:
        await context.bot.send_message(
            OWNER_ID,
            f"✅ *TagAll selesai!*\n\n👤 Pengguna: `{source_name}`\n⚙️ Mode: `{mode}`\n🕒 Durasi: 5 menit",
            parse_mode="Markdown"
        )
    except:
        pass


# ========== HANDLE PESAN ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Owner edit partner
    if context.user_data.get("waiting_for") == "partner_list" and user_id == OWNER_ID:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        lines = text.splitlines()
        for cid in lines:
            c.execute("INSERT OR REPLACE INTO partners(chat_id,is_partner,last_tag_date) VALUES(?,?,?)", (cid, 1, None))
            log_action(f"✅ Partner baru ditambahkan: {cid}")
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ {len(lines)} grup partner disimpan.")
        context.user_data["waiting_for"] = None
        return

    # Auto TagAll jika kirim link
    if "https://" in text or "t.me/" in text:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT chat_id FROM partners WHERE is_partner=1")
        partners = [r[0] for r in c.fetchall()]
        conn.close()

        if not partners:
            await update.message.reply_text("❌ Belum ada partner yang terdaftar.")
            return

        await update.message.reply_text("🚀 Auto TagAll dimulai (delay 3 detik antar grup)...")
        asyncio.create_task(tagall_process(context, user_id, partners, mode="auto"))

    # Manual TagAll dengan perintah /jalan
    if text.lower() == "/jalan":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT chat_id FROM partners WHERE is_partner=1")
        partners = [r[0] for r in c.fetchall()]
        conn.close()

        await update.message.reply_text("🚀 Manual TagAll dimulai (delay 3 detik antar grup)...")
        asyncio.create_task(tagall_process(context, chat_id, partners, mode="manual"))

# ========== RUN ==========
if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    scheduler = BackgroundScheduler()
    scheduler.add_job(reset_daily, "cron", hour=0, minute=0)
    scheduler.start()

    log_action("🚀 Bot dimulai...")
    print(f"🤖 {BOT_NAME} v{VERSION} aktif dan siap!")
    app.run_polling()
