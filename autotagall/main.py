ᴏғғ, [31/10/2025 18:01]
import logging
import asyncio
from datetime import datetime, timedelta
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from pymongo import MongoClient
from config import *

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Timezone
tz = pytz.timezone(TIMEZONE)

# Database setup
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["AutoTagAll"]
users_col = db["users"]
partners_col = db["partners"]
premium_col = db["premium"]

# ====================== COMMAND START ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_photo(
        BANNER_IMG_URL,
        caption=f"👋 Hai {user.first_name}!\n\n"
                f"Saya {BOT_NAME}.\n\n"
                "📍 Pilih mode di bawah ini:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Manual TagAll", callback_data="manual")],
            [InlineKeyboardButton("🤖 Auto TagAll", callback_data="auto")],
            [InlineKeyboardButton("👥 List Partner", callback_data="list_partner")]
        ])
    )

# ====================== MANUAL TAGALL ======================
async def manual_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("3 Menit", callback_data="durasi_3"),
         InlineKeyboardButton("5 Menit", callback_data="durasi_5")],
        [InlineKeyboardButton("10 Menit", callback_data="durasi_10"),
         InlineKeyboardButton("20 Menit", callback_data="durasi_20")],
        [InlineKeyboardButton("60 Menit", callback_data="durasi_60"),
         InlineKeyboardButton("Unlimited", callback_data="durasi_unlimited")]
    ]
    await query.edit_message_text(
        "💭 Pilih durasi untuk jalan manual TagAll:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def pilih_durasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    durasi = query.data.replace("durasi_", "")
    await query.edit_message_text(f"✅ Durasi {durasi} menit dipilih!\n\nBot akan mulai men-tag dalam grup ini...")

    # Simulasi proses TagAll
    await asyncio.sleep(5)
    await query.message.reply_text("📢 TagAll selesai! Semua anggota sudah di-tag sesuai durasi pilihanmu.")

# ====================== AUTO TAGALL ======================
async def auto_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not premium_col.find_one({"user_id": user_id}):
        await query.edit_message_text("❌ Kamu belum premium. Minta akses ke owner untuk pakai Auto TagAll.")
        return

    await query.edit_message_text(
        "🤖 Mode Auto TagAll aktif!\n\n"
        "Bot akan otomatis jalan jika admin grup sedang offline.\n"
        "Kamu bisa atur list partner di menu /addpartner"
    )

# ====================== OWNER ONLY ======================
async def add_prem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in OWNER_IDS:
        await update.message.reply_text("❌ Hanya owner yang bisa menambah premium.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Gunakan format: /addprem <user_id>")
        return

    user_id = int(context.args[0])
    premium_col.update_one({"user_id": user_id}, {"$set": {"active": True}}, upsert=True)
    await update.message.reply_text(f"✅ User {user_id} sekarang jadi premium!")

# ====================== HANDLER SETUP ======================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

ᴏғғ, [31/10/2025 18:01]
app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addprem", add_prem))
    app.add_handler(CallbackQueryHandler(manual_mode, pattern="^manual$"))
    app.add_handler(CallbackQueryHandler(auto_mode, pattern="^auto$"))
    app.add_handler(CallbackQueryHandler(pilih_durasi, pattern="^durasi_"))

    print(f"[{BOT_NAME}] Berjalan... waktu: {datetime.now(tz).strftime('%H:%M:%S')}")
    app.run_polling()

if name == "main":
    main()
