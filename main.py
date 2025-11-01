from pyrogram import Client, idle
from config import CBOT

# Import semua fitur
import manual_tagall
import auto_tagall

app = Client(
    "GarfieldBotSession",
    api_id=CBOT.API_ID,
    api_hash=CBOT.API_HASH,
    bot_token=CBOT.BOT_TOKEN
)

if name == "main":
    print("[🚀] Garfield TagAllBot starting...")
    app.start()
    print("[✅] Bot is running. Use /start in Telegram.")
    idle()
    print("[🛑] Garfield TagAllBot stopped.")
