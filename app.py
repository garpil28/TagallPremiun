import os
import asyncio
import threading
import subprocess
import time
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import (
    API_ID, API_HASH, BOT_TOKEN,
    BOT_NAME, OWNER_IDS, LOG_GROUP_ID,
    MONGO_URL, STORE_LINK, STORE_USERNAME, OWNER_USERNAME
)

# create client
app = Client(
    "GarfieldTagallSession",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

OWNER_IDS_LIST = OWNER_IDS if isinstance(OWNER_IDS, list) else ([int(OWNER_IDS)] if OWNER_IDS else [])

# auto-update repo thread
def auto_update_repo():
    while True:
        try:
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            print("[✅] Repo updated successfully.")
        except Exception as e:
            print(f"[⚠️] Repo update failed: {e}")
        time.sleep(3600)

threading.Thread(target=auto_update_repo, daemon=True).start()

# keep original start/help menu behavior (owner vs user)
@app.on_message(filters.command(["start", "help"]) & filters.private)
async def start_help(_, message):
    uid = message.from_user.id
    is_owner = uid in OWNER_IDS_LIST

    if is_owner:
        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📜 List Premium", callback_data="list_prem"),
                 InlineKeyboardButton("👥 List Partner", callback_data="list_partner")],
                [InlineKeyboardButton("➕ Add Premium", callback_data="add_prem"),
                 InlineKeyboardButton("➖ Remove Premium", callback_data="del_prem")],
                [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_all")],
                [InlineKeyboardButton("⚙️ Reload Modules", callback_data="reload_mods")],
            ]
        )
        text = (f"👑 <b>Halo Owner!</b>\n\n"
                f"Aku <b>{BOT_NAME}</b> — sistem Auto TagAll multi-bot.\n\n"
                "Gunakan menu di bawah untuk mengelola premium & partner.")
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
        text = (f"Halo {message.from_user.mention} 👋\n\n"
                f"Aku <b>{BOT_NAME}</b>. Gunakan tombol di bawah untuk akses cepat.\n\n"
                f"🔗 Setiap tag menyertakan: {STORE_LINK}")
        await message.reply_text(text, reply_markup=kb, disable_web_page_preview=True)


# delegate callbacks to garfieldbot (if present)
@app.on_callback_query()
async def _cb_handler(_, query):
    try:
        from garfieldbot import handle_callback
        await handle_callback(query)
    except Exception as e:
        await query.answer(f"Error callback: {e}", show_alert=True)


# owner admin handlers (delegates)
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


# trigger auto_tagall on t.me links (if auto_tagall present)
@app.on_message(filters.regex(r"https?://t\.me/") & filters.group)
async def _link_trigger_auto_tagall(client, message):
    try:
        from auto_tagall import trigger_auto_tagall
    except Exception as e:
        print(f"[WARN] auto_tagall trigger not available: {e}")
        return
    try:
        await trigger_auto_tagall(client, message)
    except Exception as e:
        print(f"[ERROR] trigger_auto_tagall failed: {e}")
        try:
            if LOG_GROUP_ID:
                await client.send_message(LOG_GROUP_ID, f"⚠️ trigger_auto_tagall error: {e}")
        except:
            pass


# manual tag delegate — connect to your manual_tagall.py handler (unchanged behavior)
@app.on_message(filters.command(["tagall", "utag", "mentionall"]) & filters.group)
async def _manual_tag_delegate(client, message):
    try:
        # your manual_tagall.py exposes manual_tagall_handler
        from manual_tagall import manual_tagall_handler
    except Exception as e:
        print(f"[WARN] manual_tagall handler not available: {e}")
        return

    try:
        await manual_tagall_handler(client, message)
    except Exception as e:
        print(f"[ERROR] manual_tagall failed: {e}")
        try:
            if LOG_GROUP_ID:
                await client.send_message(LOG_GROUP_ID, f"⚠️ manual_tagall error: {e}")
        except:
            pass


# safe imports to auto-load modules
def safe_import(name):
    try:
        import(name)
        print(f"✅ Loaded module: {name}")
    except Exception as e:
        print(f"⚠️ Failed to load {name}: {e}")

modules_to_load = [
    "emoji_list",
    "manual_tagall",
    "auto_tagall",
    "GarfieldBot",
    "garfieldbot",
    "menu_user",
]

for mod in modules_to_load:
    safe_import(mod)


# startup logger
async def send_start_log():
    if not LOG_GROUP_ID:
        print("⚠️ LOG_GROUP_ID not set; skipping startup log.")
        return
    try:
        await app.send_message(
            LOG_GROUP_ID,
            f"✅ <b>{BOT_NAME}</b> aktif (MAX++).\nModules: {', '.join(modules_to_load)}"
        )
    except Exception as e:
        print(f"[WARN] send_start_log error: {e}")


# runner
if name == "main":
    print(f"[🚀] Starting {BOT_NAME} ...")
    app.start()
    try:
        asyncio.get_event_loop().run_until_complete(send_start_log())
    except Exception as e:
        print(f"[!] Error during send_start_log: {e}")
    idle()
    print("[🟡] Bot stopped.")
    app.stop()
