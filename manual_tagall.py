import asyncio
import app
import random
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from emoji_list import EMOJIS

SPAM_CHATS = {}
DURATIONS = {
    "1m": 60, "3m": 180, "5m": 300, "10m": 600,
    "15m": 900, "20m": 1200, "45m": 2700,
    "90m": 5400, "120m": 7200, "360m": 21600,
}

async def is_admin(chat_id, user_id):
    admin_ids = [
        admin.user.id async for admin in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
    ]
    return user_id in admin_ids

@app.on_message(filters.command(["tagall", "utag", "mentionall"]) & filters.group)
async def tagall_handler(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ Hanya admin yang bisa pakai perintah ini.")

    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    if not text and not message.reply_to_message:
        return await message.reply("⚠️ Tambahkan teks.\nContoh: /tagall Halo semua 👋")

    SPAM_CHATS[message.chat.id] = {"text": text, "reply": message.reply_to_message}

    buttons = [
        [InlineKeyboardButton("1m", callback_data="tgallcb:1m"), InlineKeyboardButton("3m", callback_data="tgallcb:3m")],
        [InlineKeyboardButton("5m", callback_data="tgallcb:5m"), InlineKeyboardButton("10m", callback_data="tgallcb:10m")],
        [InlineKeyboardButton("Stop", callback_data="tgallcb:cancel")]
    ]
    await message.reply("🕐 Pilih durasi tagall:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("^tgallcb:"))
async def callback_tagall(_, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    user_id = cq.from_user.id
    if not await is_admin(chat_id, user_id):
        return await cq.answer("❌ Anda bukan admin!", show_alert=True)

    data = cq.data.split(":")[1]
    if data == "cancel":
        SPAM_CHATS.pop(chat_id, None)
        return await cq.message.edit("✅ TagAll dihentikan.")
    
    duration = DURATIONS.get(data)
    if not duration:
        return

    text = SPAM_CHATS[chat_id]["text"]
    reply = SPAM_CHATS[chat_id]["reply"]

    await cq.message.edit(f"▶️ TagAll dimulai selama {data}...")
    asyncio.create_task(run_tagall(chat_id, text, reply, duration))

async def run_tagall(chat_id, text, reply, duration):
    start = asyncio.get_event_loop().time()
    user_list = []
    try:
        async for m in app.get_chat_members(chat_id):
            if chat_id not in SPAM_CHATS: break
            if asyncio.get_event_loop().time() - start > duration: break
            if m.user.is_bot or m.user.is_deleted: continue

            emoji = random.choice(EMOJIS)
            mention = f"[{emoji}](tg://user?id={m.user.id})"
            user_list.append(mention)

            if len(user_list) == 5:
                msg = f"{text}\n\n{' '.join(user_list)}"
                try:
                    await app.send_message(chat_id, msg)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await app.send_message(chat_id, msg)
                await asyncio.sleep(2)
                user_list.clear()
    except Exception as e:
        await app.send_message(chat_id, f"❌ Error: {e}")
    finally:
        SPAM_CHATS.pop(chat_id, None)
        await app.send_message(chat_id, "✅ Selesai TagAll.")
