import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

# ---------------- TELEGRAM APP ----------------
tg_app = Application.builder().token(TOKEN).build()

# ---------------- BASIC HANDLERS ----------------
async def start(update, context):
    await update.message.reply_text("🎰 Token Arcade is LIVE (Webhook Mode)")

async def help_cmd(update, context):
    await update.message.reply_text("✅ Bot is working via webhook")

async def button(update, context):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🎮 Webhook system working")

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_cmd))
tg_app.add_handler(CallbackQueryHandler(button))

# ---------------- WEBHOOK ENDPOINT ----------------
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), tg_app.bot)
    tg_app.update_queue.put(update)
    return "ok"

# ---------------- SET WEBHOOK ----------------
@app.route("/setwebhook")
def set_webhook():
    url = f"{WEBHOOK_URL}/webhook/{TOKEN}"
    tg_app.bot.set_webhook(url=url)
    return f"Webhook set: {url}"

# ---------------- HEALTH CHECK ----------------
@app.route("/")
def home():
    return "BOT RUNNING (WEBHOOK MODE)"

# ---------------- START SERVER ----------------
if __name__ == "__main__":
    import threading

    def run_bot():
        tg_app.initialize()
        tg_app.start()

    threading.Thread(target=run_bot).start()

    app.run(host="0.0.0.0", port=10000)
