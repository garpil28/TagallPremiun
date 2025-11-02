# manual_tagall.py — Manual TagAll (final, preserve legacy behavior)
import asyncio
import random
from datetime import datetime
from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatMembersFilter

# import the running Client instance from app.py
from app import app
from emoji_list import EMOJIS
from config import STORE_LINK, STORE_USERNAME, OWNER_USERNAME, MONGO_URL, LOG_GROUP_ID

from pymongo import MongoClient

# Mongo (simple pymongo)
mongo = MongoClient(MONGO_URL)
db = mongo["garfield_system"]

# Required channels / owners to be joined (user must be member)
REQUIRED_USERNAMES = [STORE_USERNAME or "storegarf", OWNER_USERNAME or "kopi567"]

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
BATCH_SIZE = 5
BATCH_DELAY = 2  # seconds between batches (legacy behaviour)


async def _is_admin(chat_id: int, user_id: int) -> bool:
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
    ]
    return user_id in admin_ids


async def _check_join_all(user_id: int) -> bool:
    """
    Verify user is member of all required accounts (store + owner).
    Return True if joined all, else False.
    """
    for uname in REQUIRED_USERNAMES:
        uname = uname.lstrip("@")
        try:
            mem = await app.get_chat_member(uname, user_id)
            if mem.status not in ("member", "administrator", "creator"):
                return False
        except Exception:
            return False
    return True


# Public handler (command /tagall, /utag, /mentionall) — group only
@ app.on_message(filters.command(["tagall", "utag", "mentionall"]) & filters.group)
async def manual_tagall_handler(_, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # check admin
    if not await _is_admin(chat_id, user_id):
        return await message.reply("<blockquote>❌ Hanya admin yang bisa pakai perintah ini.</blockquote>")

    # check join required accounts
    joined = await _check_join_all(user_id)
    if not joined:
        btns = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🏪 Join Store", url=STORE_LINK)],
                [InlineKeyboardButton("👑 Owner", url=f"https://t.me/{OWNER_USERNAME}")],
            ]
        )
        return await message.reply(
            "<b>⚠️ Sebelum menggunakan TagAll, kamu harus bergabung ke Store dan mengikuti owner.</b>",
            reply_markup=btns,
            disable_web_page_preview=True,
        )

    # parse text
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    if not text and not message.reply_to_message:
        return await message.reply(
            "<blockquote><b>⚠️ Tambahkan teks.\nContoh: /utag Halo semua 👋</b></blockquote>"
        )

    SPAM_CHATS[chat_id] = {"text": text, "reply": message.reply_to_message}

    buttons = [
        [InlineKeyboardButton("1 menit", callback_data="tgallcb:1m"),
         InlineKeyboardButton("3 menit", callback_data="tgallcb:3m")],
        [InlineKeyboardButton("5 menit", callback_data="tgallcb:5m"),
         InlineKeyboardButton("10 menit", callback_data="tgallcb:10m")],
        [InlineKeyboardButton("15 menit", callback_data="tgallcb:15m"),
         InlineKeyboardButton("20 menit", callback_data="tgallcb:20m")],
        [InlineKeyboardButton("45 menit", callback_data="tgallcb:45m"),
         InlineKeyboardButton("90 menit", callback_data="tgallcb:90m")],
        [InlineKeyboardButton("120 menit", callback_data="tgallcb:120m"),
         InlineKeyboardButton("360 menit", callback_data="tgallcb:360m")],
    ]

    await message.reply("<b>Silakan pilih durasi TagAll</b>", reply_markup=InlineKeyboardMarkup(buttons))

# Callback handler (same as legacy)
@ app.on_callback_query(filters.regex("^tgallcb:"))
async def callback_tagall(_, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    user_id = cq.from_user.id

    if not await _is_admin(chat_id, user_id):
        return await cq.answer("<blockquote>❌ Maaf anda bukan admin!</blockquote>", show_alert=True)

    data = cq.data.split(":", 1)[1]

    if data == "cancel":
        if chat_id in SPAM_CHATS:
            task = SPAM_CHATS[chat_id].get("task")
            if task:
                task.cancel()
            SPAM_CHATS.pop(chat_id, None)
            await cq.message.edit_text("<blockquote>✅ Proses TagAll dihentikan oleh admin.</blockquote>")
        else:
            await cq.answer("<blockquote>⚠️ Tidak ada TagAll yg berjalan.</blockquote>", show_alert=True)
        return

    duration = DURATIONS.get(data)
    if not duration:
        return

    if "task" in SPAM_CHATS.get(chat_id, {}):
        return await cq.answer("<blockquote>⚠️ TagAll sudah berjalan.</blockquote>", show_alert=True)

    text = SPAM_CHATS[chat_id]["text"]
    reply = SPAM_CHATS[chat_id]["reply"]

    buttons = [[InlineKeyboardButton("🛑 Stop TagAll", callback_data="tgallcb:cancel")]]

    await cq.message.edit_text(
        f"▶️ TagAll dimulai selama {data} ...",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

    task = asyncio.create_task(run_tagall(chat_id, text, reply, duration, cq.message))
    SPAM_CHATS[chat_id]["task"] = task


# The core tag loop — follows original behavior (batches of 5, emojis etc)
async def run_tagall(chat_id, text, reply, duration, button_msg):
    start = asyncio.get_event_loop().time()
    user_list = []
    count = 0

    try:
        async for m in app.get_chat_members(chat_id):
            if chat_id not in SPAM_CHATS:
                break
            if asyncio.get_event_loop().time() - start > duration:
                break

            if m.user.is_bot or m.user.is_deleted:
                continue

            count += 1
            emoji = random.choice(EMOJIS)
            mention = f"[{emoji}](tg://user?id={m.user.id})"
            user_list.append(mention)

            if len(user_list) == 5:
                mention_msg = (
                    f"<blockquote>{text}</blockquote>\n\n"
                    f"<blockquote>{''.join(user_list)}</blockquote>\n\n"
                    f"<blockquote><i>{STORE_LINK}</i></blockquote>"
                )

                stop_btn = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🛑 Stop TagAll", callback_data="tgallcb:cancel")]]
                )

                try:
                    if reply:
                        await reply.reply_text(
                            mention_msg,
                            disable_web_page_preview=False,
                            reply_markup=stop_btn,
                        )
                    else:
                        await app.send_message(
                            chat_id,
                            mention_msg,
                            disable_web_page_preview=False,
                            reply_markup=stop_btn,
                        )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await app.send_message(
                        chat_id,
                        mention_msg,
                        disable_web_page_preview=False,
                        reply_markup=stop_btn,
                    )
                await asyncio.sleep(2)
                user_list.clear()

        if user_list and chat_id in SPAM_CHATS:
            mention_msg = f"{text}\n\n{''.join(user_list)}"
            stop_btn = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🛑 Stop TagAll", callback_data="tgallcb:cancel")]]
 )
            try:
                if reply:
                    await reply.reply_text(
                        mention_msg,
                        disable_web_page_preview=False,
                        reply_markup=stop_btn,
                    )
                else:
                    await app.send_message(
                        chat_id,
                        mention_msg,
                        disable_web_page_preview=False,
                        reply_markup=stop_btn,
                    )
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await app.send_message(
                    chat_id,
                    mention_msg,
                    disable_web_page_preview=False,
                    reply_markup=stop_btn,
                )

    except Exception as e:
        await app.send_message(chat_id, f"❌ Gagal: {e}")
    finally:
        if chat_id in SPAM_CHATS:
            SPAM_CHATS.pop(chat_id, None)

        try:
            await button_msg.edit_reply_markup(None)
        except:
            pass

        await app.send_message(chat_id, f"<blockquote>✅ Selesai TagAll, total {count} anggota.</blockquote>")
