# ===============================================
# GarfieldBot.py — core tagall & partner manager
# ===============================================
import asyncio
import random
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_NAME, LOG_GROUP_ID, OWNER_IDS
from emoji_list import EMOJIS

# status global
ACTIVE_TAGS = {}
PARTNER_LIST = {}
PREMIUM_USERS = set()

TAG_BATCH = 6       # jumlah user per post
SPAM_DELAY = 5      # delay antar kirim batch
USER_FOOTER = "\n\n🐾 Powered by [Garfield](https://t.me/storegarf)"

# ────────────────────────────────────────────────
# Fungsi tagall dasar
# ────────────────────────────────────────────────
async def tagall_run(app: Client, chat_id: int, duration: int):
    try:
        members = []
        async for m in app.get_chat_members(chat_id):
            if m.user.is_bot or m.user.is_deleted:
                continue
            emoji = random.choice(EMOJIS)
            members.append(f"{emoji} [{m.user.first_name}](tg://user?id={m.user.id})")

        chunks = [members[i:i + TAG_BATCH] for i in range(0, len(members), TAG_BATCH)]
        end_time = datetime.now().timestamp() + duration
        while datetime.now().timestamp() < end_time:
            for batch in chunks:
                msg = f"✨ <b>{BOT_NAME}</b> TagAll Reminder!\n" + "\n".join(batch) + USER_FOOTER
                await app.send_message(chat_id, msg, disable_web_page_preview=True)
                await asyncio.sleep(SPAM_DELAY)
        await app.send_message(chat_id, "✅ Sesi tagall selesai otomatis.")
    except Exception as e:
        await app.send_message(chat_id, f"❌ Error TagAll: {e}")

# ────────────────────────────────────────────────
# Handler minta tagall
# ────────────────────────────────────────────────
async def request_tagall(app: Client, user_id: int, chat_id: int):
    if chat_id in ACTIVE_TAGS:
        await app.send_message(chat_id, "⚠️ TagAll sedang berjalan.")
        return
    ACTIVE_TAGS[chat_id] = True
    duration = 300 if user_id in PARTNER_LIST else 120
    await app.send_message(chat_id, f"🟢 TagAll dimulai ({duration//60} menit).")
    await tagall_run(app, chat_id, duration)
    ACTIVE_TAGS.pop(chat_id, None)

# ────────────────────────────────────────────────
# Ping Command
# ────────────────────────────────────────────────
async def ping_cmd(app: Client, message: Message):
    start = datetime.now()
    msg = await message.reply_text("🏓 Pong...")
    end = datetime.now()
    ping = (end - start).microseconds / 1000
    await msg.edit_text(f"🏓 Pong! `{ping}ms`")

# ────────────────────────────────────────────────
# Callback handler delegasi dari app.py
# ────────────────────────────────────────────────
async def handle_callback(query):
    data = query.data
    user = query.from_user
    app = query._client

    if data == "req_tagall":
        if query.message.chat.type == enums.ChatType.PRIVATE:
            await query.answer("❌ Minta TagAll hanya bisa di grup.", show_alert=True)
            return
        await query.answer("🕐 Mulai tagall sebentar...", show_alert=True)
        await request_tagall(app, user.id, query.message.chat.id)

    elif data == "req_partner":
        PARTNER_LIST[user.id] = True
        await query.answer("🤝 Kamu kini partner GarfieldBot!", show_alert=True)
        await query.message.reply(f"✅ {user.mention} jadi partner resmi GarfieldBot.")

    elif data == "req_unpartner":
        PARTNER_LIST.pop(user.id, None)
        await query.answer("❌ Partner dilepas.", show_alert=True)
        await query.message.reply(f"⚙️ {user.mention} bukan partner lagi.")

    elif data == "req_help":
        await query.answer("📘 Panduan dikirim.", show_alert=False)
        await query.message.reply(
            "<b>Panduan Penggunaan:</b>\n"
            "• /start — buka menu\n"
            "• /ping — cek kecepatan bot\n"
            "• Tombol 'Minta TagAll' — tag semua member grup\n"
            "• Partner aktif: 5 menit\n"
            "• Non-partner: 2 menit\n"
            f"{USER_FOOTER}",
            disable_web_page_preview=True,
        )

    elif data == "reload_mods":
        if user.id not in OWNER_IDS:
            await query.answer("❌ Akses ditolak.", show_alert=True)
            return
        await query.answer("♻️ Reload module...", show_alert=False)
        os.system("python3 app.py")

    else:
        await query.answer("⚙️ Tidak dikenal.", show_alert=True)
