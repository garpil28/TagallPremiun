from pyrogram import Client, idle
from config import CBOT

# === GarfieldBot App ===
app = Client(
    "GarfieldBotSession",
    api_id=CBOT.API_ID,
    api_hash=CBOT.API_HASH,
    bot_token=CBOT.BOT_TOKEN
)

# Import modul setelah app dibuat
import manual_tagall
import auto_tagall
import garfieldbot  # start, ping, partner menu, dll

if name == "main":
    print("[🚀] GarfieldBot starting...")
    app.start()
    print("[✅] Bot aktif. Gunakan /start di Telegram.")
    idle()
    print("[🛑] GarfieldBot stopped.")
