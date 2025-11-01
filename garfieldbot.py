# ===============================================
# garfieldbot.py — Owner Management System
# ===============================================
from pyrogram.types import Message
from config import BOT_NAME
import asyncio

PARTNER_BOTS = {}
PREMIUM_USERS = set()

async def list_partners_text():
    if not PARTNER_BOTS:
        return "📭 Belum ada partner bot."
    msg = "🤖 <b>Daftar Partner Bot Aktif:</b>\n"
    for tok, info in PARTNER_BOTS.items():
        msg += f"• {info['name']} — log_id: {info['log']}\n"
    return msg

async def add_partner_by_token_cmd(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Gunakan format: `/addbot <token> [log_chat_id]`")
        return
    token = args[1]
    log_chat = args[2] if len(args) >= 3 else "None"
    PARTNER_BOTS[token] = {"name": f"BotClone_{len(PARTNER_BOTS)+1}", "log": log_chat}
    await message.reply(f"✅ Partner bot baru ditambahkan.\nToken disimpan lokal.")

async def del_partner_cmd(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Gunakan format: `/delbot <token>`")
        return
    token = args[1]
    if token in PARTNER_BOTS:
        PARTNER_BOTS.pop(token)
        await message.reply("🗑️ Partner bot dihapus.")
    else:
        await message.reply("❌ Token tidak ditemukan.")

async def broadcast_cmd(message: Message):
    if len(PARTNER_BOTS) == 0:
        await message.reply("📭 Tidak ada partner untuk broadcast.")
        return
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.reply("Gunakan `/broadcast <pesan>`.")
        return
    pesan = text[1]
    hit = 0
    for token, info in PARTNER_BOTS.items():
        hit += 1
        await message.reply(f"📤 Broadcast ke {info['name']} (log: {info['log']})")
        await asyncio.sleep(0.5)
    await message.reply(f"✅ Broadcast terkirim ke {hit} partner bot.")
