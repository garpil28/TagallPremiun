import asyncio
import random
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from app import app
from emoji_list import EMOJIS

SPAM_CHATS = {}
DURATIONS = {
    "1m": 60,
    "3m": 180,
    "5m": 300,
    "10m": 600,
    "15m": 900,
    "20m": 1200,
    "45m": 2700,
    "90m": 5400,
    "120m": 7200,
    "360m": 21600,
}

# ─── CEK WAJIB JOIN CHANNEL ──────────────────────
async def is_joined(user_id):
    try:
        member = await app.get_chat_member("@storegarf", user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

# ─── CEK ADMIN ───────────────────────────────────
async def is_admin(chat_id, user_id):
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
    ]
    return user_id in admin_ids

# ─── COMMAND TAGALL / UTAG ───────────────────────
@app.on_message(filters.command(["tagall", "utag", "mentionall"]) & filters.group)
async def tagall_handler(_, message: Message):
    user_id = message.from_user.id

    if not await is_admin(message.chat.id, user_id):
        return await message.reply("<blockquote>❌ Hanya admin yang bisa pakai perintah ini.</blockquote>")

    if not await is_joined(user_id):
        return await message.reply(
            "<b>⚠️ Kamu belum join ke channel owner bot.</b>\n\n"
            "Silakan join dulu untuk bisa menggunakan fitur tagall.\n\n"
            "🔗 [Gabung ke Store Owner](https://t.me/storegarf)",
            disable_web_page_preview=True,
        )

    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    if not text and not message.reply_to_message:
        return await message.reply("<b>⚠️ Tambahkan teks!\nContoh:</b> /utag Halo semua 👋")

    SPAM_CHATS[message.chat.id] = {"text": text, "reply": message.reply_to_message}

    buttons = [
        [InlineKeyboardButton("1 menit", callback_data="tgallcb:1m"), InlineKeyboardButton("3 menit", callback_data="tgallcb:3m")],
        [InlineKeyboardButton("5 menit", callback_data="tgallcb:5m"), InlineKeyboardButton("10 menit", callback_data="tgallcb:10m")],
        [InlineKeyboardButton("15 menit", callback_data="tgallcb:15m"), InlineKeyboardButton("20 menit", callback_data="tgallcb:20m")],
        [InlineKeyboardButton("45 menit", callback_data="tgallcb:45m"), InlineKeyboardButton("90 menit", callback_data="tgallcb:90m")],
        [InlineKeyboardButton("120 menit", callback_data="tgallcb:120m"), InlineKeyboardButton("360 menit", callback_data="tgallcb:360m")],
    ]

    await message.reply("<b>⏱ Pilih durasi TagAll:</b>", reply_markup=InlineKeyboardMarkup(buttons))

# ─── CALLBACK TAGALL ─────────────────────────────
@app.on_callback_query(filters.regex("^tgallcb:"))
async def callback_tagall(_, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    user_id = cq.from_user.id

    if not await is_admin(chat_id, user_id):
        return await cq.answer("❌ Hanya admin yang bisa mengatur tagall.", show_alert=True)

    data = cq.data.split(":", 1)[1]
    if data == "cancel":
        if chat_id in SPAM_CHATS:
            task = SPAM_CHATS[chat_id].get("task")
            if task:
                task.cancel()
            SPAM_CHATS.pop(chat_id, None)
            await cq.message.edit_text("🛑 TagAll dihentikan oleh admin.")
        else:
            await cq.answer("⚠️ Tidak ada tagall yang berjalan.", show_alert=True)
        return

    duration = DURATIONS.get(data)
    if not duration:
        return await cq.answer("❌ Durasi tidak dikenal.", show_alert=True)

    if "task" in SPAM_CHATS.get(chat_id, {}):
        return await cq.answer("⚠️ TagAll sudah berjalan.", show_alert=True)

    text = SPAM_CHATS[chat_id]["text"]
    reply = SPAM_CHATS[chat_id]["reply"]

await cq.message.edit_text(
        f"▶️ <b>TagAll dimulai selama {data}.</b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Stop", callback_data="tgallcb:cancel")]]),
    )

    task = asyncio.create_task(run_tagall(chat_id, text, reply, duration, cq.message))
    SPAM_CHATS[chat_id]["task"] = task

# ─── JALANKAN TAGALL ─────────────────────────────
async def run_tagall(chat_id, text, reply, duration, button_msg):
    start = asyncio.get_event_loop().time()
    user_list, count = [], 0

    try:
        async for m in app.get_chat_members(chat_id):
            if chat_id not in SPAM_CHATS or asyncio.get_event_loop().time() - start > duration:
                break
            if m.user.is_bot or m.user.is_deleted:
                continue

            count += 1
            emoji = random.choice(EMOJIS)
            user_list.append(f"[{emoji}](tg://user?id={m.user.id})")

            if len(user_list) == 5:
                msg_text = (
                    f"<blockquote>{text}</blockquote>\n\n"
                    f"<blockquote>{' '.join(user_list)}</blockquote>\n\n"
                    f"<blockquote>🔗 <i>@storegarf — Official Store</i></blockquote>"
                )

                try:
                    if reply:
                        await reply.reply_text(msg_text, disable_web_page_preview=True)
                    else:
                        await app.send_message(chat_id, msg_text, disable_web_page_preview=True)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await app.send_message(chat_id, msg_text, disable_web_page_preview=True)

                user_list.clear()
                await asyncio.sleep(2)

        await app.send_message(chat_id, f"✅ Selesai TagAll — total {count} member disebut.")
    except Exception as e:
        await app.send_message(chat_id, f"❌ Error: {e}")
    finally:
        SPAM_CHATS.pop(chat_id, None)
        try:
            await button_msg.edit_reply_markup(None)
        except:
            pass

# ─── COMMAND CANCEL ──────────────────────────────
@app.on_message(filters.command(["cancel", "stopmention", "cancelall"]) & filters.group)
async def cancel_cmd(_, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return
    if message.chat.id in SPAM_CHATS:
        SPAM_CHATS.pop(message.chat.id, None)
        await message.reply("✅ TagAll dihentikan manual.")
    else:
        await message.reply("⚠️ Tidak ada TagAll yang berjalan.")

MODULE = "TagAll"
HELP = """
<b>Perintah Manual TagAll:</b>

• /tagall [teks]
• /utag [teks]
• /mentionall [teks]
  ↳ Menandai semua member grup.

• /cancel atau /stopmention
  ↳ Hentikan proses TagAll yang sedang berjalan.

⚠️ Hanya admin yang dapat menggunakan perintah ini.
📎 Wajib join ke @storegarf untuk aktivasi fitur.
"""
