from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def home(u):
    return (
        f"🎰 TOKEN ARCADE\n"
        f"━━━━━━━━━━━━\n"
        f"💰 {u['coins']}\n"
        f"⚡ Lv {u['level']}\n"
        f"🔥 Streak {u.get('streak',0)}"
    )

def home_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Games", callback_data="games")],
        [InlineKeyboardButton("🏆 Leaderboards", callback_data="lb")],
        [InlineKeyboardButton("🔥 Live Feed", callback_data="feed")]
    ])

def games_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Dice", callback_data="dice"),
         InlineKeyboardButton("🎯 Darts", callback_data="darts")],
        [InlineKeyboardButton("🏀 Basket", callback_data="basket"),
         InlineKeyboardButton("🎳 Bowling", callback_data="bowling")],
        [InlineKeyboardButton("⚽ Football", callback_data="football")],
        [InlineKeyboardButton("💣 Mines", callback_data="mines")],
        [InlineKeyboardButton("🎱 Keno", callback_data="keno")],
        [InlineKeyboardButton("⬅ Back", callback_data="home")]
    ])
