from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import TOKEN
from storage import load, get, save
from ui import home, home_kb, games_kb
from games import dice, darts, basket, bowling, football

async def start(update, context):
    u = get(update.effective_user.id)
    save()
    await update.message.reply_text(home(u), reply_markup=home_kb())

async def cb(update, context):
    q = update.callback_query
    await q.answer()

    u = get(q.from_user.id)

    if q.data == "home":
        await q.edit_message_text(home(u), reply_markup=home_kb())

    elif q.data == "games":
        await q.edit_message_text("🎮 GAMES", reply_markup=games_kb())

    elif q.data == "dice":
        await dice(update, context)

    elif q.data == "darts":
        await darts(update, context)

    elif q.data == "basket":
        await basket(update, context)

    elif q.data == "bowling":
        await bowling(update, context)

    elif q.data == "football":
        await football(update, context)

def main():
    load()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb))

    print("BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
