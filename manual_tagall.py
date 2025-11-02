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

# ─── Wajib Join Channel  ─────────────────
REQUIRED_CHANNELS = [
    "https://t.me/storegarf",
    
]

async def check_join_status(app, user_id):
    for ch in REQUIRED_CHANNELS:
        username = ch.replace("https://t.me/", "")
        try:
            member = await app.get_chat_member(username, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True


# ─── DATA DASAR ────────────────────────────────
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


async def is_admin(chat_id, user_id):
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(
            chat_id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]
    return user_id in admin_ids


# ─── Command /tagall ─────────────────────────────
@app.on_message(filters.command(["tagall", "utag", "mentionall"]) & filters.group)
async def tagall_handler(_, message: Message):

    # 🔐 Wajib join Garfield Store & Owner
    joined = await check_join_status(app, message.from_user.id)
    if not joined:
        btns = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📢 Join Garfield Store", url="https://t.me/GarfieldStore")],
                [InlineKeyboardButton("👑 Owner", url="https://t.me/GarfieldOwner")],
            ]
        )
        return await message.reply(
            "<b>⚠️ Wajib join channel sebelum pakai fitur ini!</b>",
            reply_markup=btns,
        )

    # 🔰 Hanya admin yang bisa pakai
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("<blockquote>❌ Hanya admin yang bisa pakai perintah ini.</blockquote>")

    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    if not text and not message.reply_to_message:
        return await message.reply(
            "<blockquote><b>⚠️ Tambahkan teks.\nContoh: /utag Halo semua 👋</b></blockquote>"
        )

    SPAM_CHATS[message.chat.id] = {
        "text": text,
        "reply": message.reply_to_message,
    }

    buttons = [
        [
            InlineKeyboardButton("1 menit", callback_data="tgallcb:1m"),
            InlineKeyboardButton("3 menit", callback_data="tgallcb:3m"),
        ],
        [
            InlineKeyboardButton("5 menit", callback_data="tgallcb:5m"),
            InlineKeyboardButton("10 menit", callback_data="tgallcb:10m"),
        ],
        [
            InlineKeyboardButton("15 menit", callback_data="tgallcb:15m"),
            InlineKeyboardButton("20 menit", callback_data="tgallcb:20m"),
        ],
        [
            InlineKeyboardButton("45 menit", callback_data="tgallcb:45m"),
            InlineKeyboardButton("90 menit", callback_data="tgallcb:90m"),
        ],
        [
            InlineKeyboardButton("120 menit", callback_data="tgallcb:120m"),
            InlineKeyboardButton("360 menit", callback_data="tgallcb:360m"),
        ],
    ]

    await message.reply(
        "<b>Silakan pilih durasi TagAll</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ─── Callback khusus tgallcb ─────────────────────
@app.on_callback_query(filters.regex("^tgallcb:"))
async def callback_tagall(_, cq: CallbackQuery):
    chat_id = cq.message.chat.id
    user_id = cq.from_user.id

    if not await is_admin(chat_id, user_id):
        return await cq.answer("<blockquote>❌ Maaf anda bukan admin!</blockquote>", show_alert=True)

    data = cq.data.split(":", 1)[1]
