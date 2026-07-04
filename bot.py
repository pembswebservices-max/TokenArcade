import os
import json
import random
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATA_FILE = "data.json"

# ---------------- STORAGE ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        return json.load(open(DATA_FILE))
    return {}

def save_data():
    json.dump(users, open(DATA_FILE, "w"), indent=2)

users = load_data()

def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "coins": 1000,
            "xp": 0,
            "last_daily": None,
            "games": 0
        }
    return users[uid]

# ---------------- UI ----------------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Play Games", callback_data="games")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")]
    ])

def games_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Dice", callback_data="dice")],
        [InlineKeyboardButton("🎯 Darts", callback_data="darts")],
        [InlineKeyboardButton("🏀 Basket", callback_data="basket")],
        [InlineKeyboardButton("⬅ Back", callback_data="home")]
    ])

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    save_data()

    await update.message.reply_text(
        f"🎰 SIMPLE ARCADE BOT\n\n💰 Coins: {user['coins']}\n⚡ XP: {user['xp']}",
        reply_markup=main_menu()
    )

# ---------------- DAILY ----------------
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    today = str(datetime.now().date())

    if user["last_daily"] == today:
        await update.message.reply_text("❌ Already claimed today.")
        return

    user["coins"] += 200
    user["last_daily"] = today
    save_data()

    await update.message.reply_text("✅ Daily +200 coins!")

# ---------------- CALLBACK ----------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user = get_user(q.from_user.id)

    # HOME
    if q.data == "home":
        await q.edit_message_text(
            f"🎰 MAIN MENU\n\n💰 {user['coins']} coins",
            reply_markup=main_menu()
        )

    # GAMES MENU
    elif q.data == "games":
        await q.edit_message_text("🎮 Choose a game:", reply_markup=games_menu())

    # BALANCE
    elif q.data == "balance":
        await q.edit_message_text(
            f"💰 BALANCE\n\nCoins: {user['coins']}\nXP: {user['xp']}\nGames: {user['games']}",
            reply_markup=main_menu()
        )

    # LEADERBOARD
    elif q.data == "leaderboard":
        top = sorted(users.items(), key=lambda x: x[1]["coins"], reverse=True)[:5]
        text = "🏆 LEADERBOARD\n\n"
        for i, (uid, u) in enumerate(top, 1):
            text += f"{i}. User {uid[:4]} — {u['coins']} coins\n"

        await q.edit_message_text(text, reply_markup=main_menu())

    # ---------------- GAMES ----------------
    elif q.data == "dice":
        await play_dice(q, user)

    elif q.data == "darts":
        await play_darts(q, user)

    elif q.data == "basket":
        await play_basket(q, user)

    save_data()

# ---------------- GAMES ----------------
async def play_dice(q, user):
    msg = await q.message.reply_dice("🎲")
    roll = msg.dice.value

    win = roll >= 4
    reward = 200 if win else -100

    user["coins"] += reward
    user["xp"] += 10
    user["games"] += 1

    await q.message.reply_text(
        f"🎲 Dice: {roll}\n"
        f"{'✅ WIN +200' if win else '❌ LOSE -100'}"
    )

async def play_darts(q, user):
    msg = await q.message.reply_dice("🎯")
    roll = msg.dice.value

    win = roll >= 5
    reward = 250 if win else -100

    user["coins"] += reward
    user["xp"] += 10
    user["games"] += 1

    await q.message.reply_text(
        f"🎯 Darts: {roll}\n"
        f"{'✅ WIN +250' if win else '❌ LOSE -100'}"
    )

async def play_basket(q, user):
    msg = await q.message.reply_dice("🏀")
    roll = msg.dice.value

    win = roll >= 4
    reward = 300 if win else -100

    user["coins"] += reward
    user["xp"] += 10
    user["games"] += 1

    await q.message.reply_text(
        f"🏀 Basket: {roll}\n"
        f"{'✅ WIN +300' if win else '❌ LOSE -100'}"
    )

# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CallbackQueryHandler(buttons))

    print("BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
