import asyncio
import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatMembersFilter
from app import app
from config import OWNER_IDS

EMOJIS = ["🔥","😎","✅","👻","💥","⚡","🌟","🐱"]

SPAM_CHATS = {}  # chat_id -> {"text":..., "reply": Message or None, "task": Task}

DURATIONS = {
    "1m": 60, "3m": 180, "5m": 300, "10m": 600,
    "15m": 900, "20m": 1200, "45m": 2700, "90m": 5400,
    "120m": 7200, "360m": 21600, "unlimited": None
}

async def is_admin(chat_id: int, user_id: int) -> bool:
    admin_ids = [a.user.id async for a in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)]
    return user_id in admin_ids or user_id in OWNER_IDS

@ app.on_message(filters.command(["tagall","all","mentionall","utag"]) & filters.group)
async def tagall_handler(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ Hanya admin yang bisa pakai perintah ini.")
    text = message.text.split(None,1)[1] if len(message.command) > 1 else ""
    if not text and not message.reply_to_message:
        return await message.reply("⚠️ Tambahkan teks.\nContoh: /tagall Halo semua!")
    SPAM_CHATS[message.chat.id] = {"text": text, "reply": message.reply_to_message}
    buttons = [
        [InlineKeyboardButton("1m", "tgallcb:1m"), InlineKeyboardButton("3m", "tgallcb:3m")],
        [InlineKeyboardButton("5m", "tgallcb:5m"), InlineKeyboardButton("10m", "tgallcb:10m")],
        [InlineKeyboardButton("15m", "tgallcb:15m"), InlineKeyboardButton("30m", "tgallcb:30m")],
        [InlineKeyboardButton("60m", "tgallcb:60m"), InlineKeyboardButton("Unlimited", "tgallcb:unlimited")],
        [InlineKeyboardButton("Stop", "tgallcb:cancel")]
    ]
    await message.reply("🕐 Pilih durasi TagAll:", reply_markup=InlineKeyboardMarkup(buttons))

@ app.on_callback_query(filters.regex("^tgallcb:"))
async def callback_tagall(_, cq):
    chat_id = cq.message.chat.id
    user_id = cq.from_user.id
    if not await is_admin(chat_id, user_id):
        return await cq.answer("❌ Anda bukan admin!", show_alert=True)
    key = cq.data.split(":",1)[1]
    if key == "cancel":
        task = SPAM_CHATS.get(chat_id, {}).get("task")
        if task:
            task.cancel()
        SPAM_CHATS.pop(chat_id, None)
        await cq.message.edit("✅ Proses TagAll dihentikan.")
        return
    duration = DURATIONS.get(key)
    if chat_id in SPAM_CHATS and SPAM_CHATS[chat_id].get("task"):
        return await cq.answer("⚠️ TagAll sudah berjalan.", show_alert=True)
    text = SPAM_CHATS[chat_id]["text"]
    reply = SPAM_CHATS[chat_id]["reply"]
    await cq.message.edit(f"▶️ TagAll dimulai selama {key} ...")
    task = asyncio.create_task(run_tagall(chat_id, text, reply, duration, cq.message))
    SPAM_CHATS[chat_id]["task"] = task

async def run_tagall(chat_id, text, reply, duration, button_msg):
    start = asyncio.get_event_loop().time()
    user_batch = []
    count = 0
    try:
        async for m in app.get_chat_members(chat_id):
            if chat_id not in SPAM_CHATS:
                break
            if duration and (asyncio.get_event_loop().time() - start > duration):
                break
            if m.user.is_bot or m.user.is_deleted:
                continue
            count += 1
            emoji = random.choice(EMOJIS)
            user_batch.append(f"[{emoji}](tg://user?id={m.user.id})")
            if len(user_batch) >= 5:
                msg = f"{text}\n\n{' '.join(user_batch)}"
                try:
                    if reply:
                        await reply.reply_text(msg, disable_web_page_preview=True)
                    else:
                        
await app.send_message(chat_id, msg, disable_web_page_preview=True)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await app.send_message(chat_id, msg, disable_web_page_preview=True)
                await asyncio.sleep(2)  # jeda batch
                user_batch = []
        if user_batch and chat_id in SPAM_CHATS:
            msg = f"{text}\n\n{' '.join(user_batch)}"
            try:
                if reply:
                    await reply.reply_text(msg, disable_web_page_preview=True)
                else:
                    await app.send_message(chat_id, msg, disable_web_page_preview=True)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await app.send_message(chat_id, msg, disable_web_page_preview=True)
    except Exception as e:
        await app.send_message(chat_id, f"❌ Gagal: {e}")
    finally:
        SPAM_CHATS.pop(chat_id, None)
        try:
            await button_msg.edit_reply_markup(None)
        except:
            pass
        await app.send_message(chat_id, f"✅ Selesai TagAll, total {count} anggota.")
