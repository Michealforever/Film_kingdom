import json
import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.ext import Defaults

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load config from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")
ADMINS = os.environ.get("ADMINS", "").split(",")  # comma-separated user IDs

bot = Bot(token=BOT_TOKEN)

application = Application.builder().token(BOT_TOKEN).build()

# Watermarked file handler
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in ADMINS:
        return

    file = update.message.document or update.message.video or update.message.audio or update.message.photo[-1]
    caption = (update.message.caption or "") + f"\n\n📌 From: {CHANNEL_USERNAME}"

    if hasattr(file, 'file_id'):
        await context.bot.send_document(chat_id=CHANNEL_USERNAME, document=file.file_id, caption=caption)
    else:
        await update.message.reply_text("Unsupported file type.")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running. Send your file to forward it with watermark.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.ALL, handle_file))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is alive!"

if __name__ == "__main__":
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=f"https://{os.environ.get('RENDER_URL')}/{BOT_TOKEN}"
)
  
