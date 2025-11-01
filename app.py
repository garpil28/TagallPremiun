# ===============================================
# Garfield Auto TagAll — Multi Bot System (Full)
# ===============================================

import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    API_ID, API_HASH, BOT_TOKEN,
    BOT_NAME, OWNER_IDS, LOG_GROUP_ID
)

# ────────────────────────────────────────────────
# Init Client
# ────────────────────────────────────────────────
app = Client(
    "GarfieldTagallSession",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# normalize owner list
OWNER_IDS_LIST = OWNER_IDS if isinstance(OWNER_IDS, list) else (
    [int(OWNER_IDS)] if OWNER_IDS else []
)

# ────────────────────────────────────────────────
# Start & Help Handler (Interactive Menu)
# ────────────────────────────────────────────────
@app.on_message(filters.command(["start", "help"]) & filters.private)
async def start_help(_, message):
    uid = message.from_user.id
    is_owner = uid in OWNER_IDS_LIST

    if is_owner:
        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📜 List Premium", callback_data="list_prem"),
                    InlineKeyboardButton("👥 List Partner", callback_data="list_partner"),
                ],
                [
                    InlineKeyboardButton("➕ Add Premium", callback_data="add_prem"),
                    InlineKeyboardButton("➖ Remove Premium", callback_data="del_prem"),
                ],
                [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_all")],
                [InlineKeyboardButton("⚙️ Reload Modules", callback_data="reload_mods")],
            ]
        )
        text = (
            f"👑 <b>Halo Owner!</b>\n\n"
            f"Aku <b>{BOT_NAME}</b> — sistem Auto TagAll multi-bot.\n\n"
            f"Gunakan menu di bawah untuk mengelola premium & partner.\n"
            f"🧩 Semua event, request partner, dan log tercatat otomatis di grup log."
        )
        await message.reply_text(text, reply_markup=kb, disable_web_page_preview=True)

    else:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📢 Minta TagAll", callback_data="req_tagall")],
                [InlineKeyboardButton("🤝 Ajukan Partner", callback_data="req_partner")],
                [InlineKeyboardButton("❌ Lepas Partner", callback_data="req_unpartner")],
                [InlineKeyboardButton("🆘 Bantuan", callback_data="req_help")],
            ]
        )
        text = (
            f"Halo {message.from_user.mention} 👋\n\n"
            f"Aku <b>{BOT_NAME}</b>.\n"
            f"Gunakan tombol di bawah untuk:\n"
            f"— Minta tagall otomatis (2 menit untuk user biasa, 5 menit untuk partner)\n"
            f"— Ajukan partner agar bisa minta tagall kapan pun\n"
            f"— Lepas hubungan partner jika sudah tidak digunakan\n\n"
            f"🔗 Setiap tag akan menyertakan footer tautan:\n"
            f"<code>https://t.me/storegarf</code>"
        )
        await message.reply_text(text, reply_markup=kb, disable_web_page_preview=True)

# ────────────────────────────────────────────────
# Callback Delegator
# ────────────────────────────────────────────────
@app.on_callback_query()
async def _cb_handler(_, query):
    try:
        from garfieldbot import handle_callback
        await handle_callback(query)
    except Exception as e:
        await query.answer(f"Error callback: {e}", show_alert=True)

# ────────────────────────────────────────────────
# Owner Commands (manual CLI inside Telegram)
# ────────────────────────────────────────────────
@app.on_message(filters.command("listbot") & filters.user(OWNER_IDS_LIST))
async def list_bot(_, message):
    try:
        from garfieldbot import list_partners_text
        await message.reply_text(await list_partners_text())
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("addbot") & filters.user(OWNER_IDS_LIST))
async def add_bot(_, message):
    try:
        from garfieldbot import add_partner_by_token_cmd
        await add_partner_by_token_cmd(message)
    except Exception as e:
        await message.reply_text(f"❌ Error addbot: {e}")

@app.on_message(filters.command("delbot") & filters.user(OWNER_IDS_LIST))
async def del_bot(_, message):
    try:
        from garfieldbot import del_partner_cmd
        await del_partner_cmd(message)
    except Exception as e:
        await message.reply_text(f"❌ Error delbot: {e}")

@app.on_message(filters.command("broadcast") & filters.user(OWNER_IDS_LIST))
async def broadcast(_, message):
    try:
        from garfieldbot import broadcast_cmd
        await broadcast_cmd(message)
    except Exception as e:
        await message.reply_text(f"❌ Error broadcast: {e}")

# ────────────────────────────────────────────────
# Imports (safe, after client creation)
# ────────────────────────────────────────────────
def safe_import(name):
    try:
        __import__(name)
        print(f"✅ Loaded module: {name}")
    except Exception as e:
        print(f"⚠️ Failed to load {name}: {e}")

for mod in ["emoji_list", "manual_tagall", "auto_tagall", "GarfieldBot", "garfieldbot"]:
    safe_import(mod)

# ────────────────────────────────────────────────
# Startup Logger
# ────────────────────────────────────────────────
async def send_start_log():
    if not LOG_GROUP_ID:
        print("⚠️ LOG_GROUP_ID not set; skipping startup log.")
        return
    try:
        await app.send_message(
            LOG_GROUP_ID,
            f"✅ <b>{BOT_NAME}</b> aktif.\nMode: <code>multi-partner / owner-hosted</code>\n"
            f"Semua module berhasil dimuat ✅"
        )
        print("[LOG] Startup message sent.")
    except Exception as e:
        print(f"[WARN] send_start_log error: {e}")

# ────────────────────────────────────────────────
# Runner
# ────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[🚀] Starting {BOT_NAME} ...")
    app.start()
    print("[✅] Bot running — CTRL+C to stop.")
    try:
        asyncio.get_event_loop().run_until_complete(send_start_log())
    except Exception as e:
        print(f"[!] Error during send_start_log: {e}")
    idle()
    print("[🟡] Bot stopped.")
    app.stop()
