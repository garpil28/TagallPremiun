from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils import log_to_group, get_wib_time

# ========== MODE MANUAL TAGALL ==========
async def jalan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("3 menit", callback_data="durasi_3"),
         InlineKeyboardButton("5 menit", callback_data="durasi_5")],
        [InlineKeyboardButton("10 menit", callback_data="durasi_10"),
         InlineKeyboardButton("20 menit", callback_data="durasi_20")],
        [InlineKeyboardButton("40 menit", callback_data="durasi_40"),
         InlineKeyboardButton("60 menit", callback_data="durasi_60")],
        [InlineKeyboardButton("90 menit", callback_data="durasi_90"),
         InlineKeyboardButton("Unlimited", callback_data="durasi_unlimited")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🧠 Pilih durasi jalan manual untuk TagAll:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("durasi_"):
        durasi = data.split("_")[1]
        if durasi == "unlimited":
            menit = 999999
        else:
            menit = int(durasi)

        await query.edit_message_text(f"⏳ TagAll berjalan selama {menit} menit...")

        await log_to_group(context.bot, f"👑 Manual TagAll dimulai oleh {query.from_user.full_name} di grup {query.message.chat.title} selama {menit} menit ({get_wib_time()})")

        # Jalankan fungsi tagall (buat simulasi dulu)
        await context.bot.send_message(query.message.chat.id, f"🔥 TagAll manual aktif selama {menit} menit!")

        # Setelah selesai
        await context.bot.send_message(query.message.chat.id, f"✅ TagAll selesai dalam {menit} menit!")
