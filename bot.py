import os
import json
import logging
import asyncio
import random
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from flask import Flask, request

# ===================== CONFIG =====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 8000))
DATA_FILE = 'arcade_users.json'

if not TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN not set")
if not WEBHOOK_URL:
    raise ValueError("❌ WEBHOOK_URL not set")

# ===================== FLASK APP =====================
flask_app = Flask(__name__)

# ===================== BOT APPLICATION =====================
# This is initialized once per process
bot_app: Optional[Application] = None

# ===================== STORAGE =====================
def load_users() -> dict:
    """Load users from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading users: {e}")
    return {}

def save_users(users: dict) -> None:
    """Save users to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving users: {e}")

def get_user(user_id: int, users: dict) -> dict:
    """Get or create user"""
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            'coins': 500,
            'xp': 0,
            'ref_code': f"TG{user_id % 10000:04d}",
            'referrals': [],
            'stats': {
                'games_played': 0,
                'total_wagered': 0,
                'biggest_win': 0,
                'last_daily': None,
            }
        }
        save_users(users)
    return users[uid]

# ===================== HANDLERS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command - main menu"""
    users = load_users()
    user = get_user(update.effective_user.id, users)
    
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data='balance')],
        [InlineKeyboardButton("📊 Profile", callback_data='profile')],
        [InlineKeyboardButton("🎲 Dice", callback_data='dice_demo')],
        [InlineKeyboardButton("🎰 Slots", callback_data='slots_demo')],
        [InlineKeyboardButton("💣 Mines", callback_data='mines_info')],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data='leaderboard')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎰 *TokenArcade on Telegram!*\n\n"
        f"Hi {update.effective_user.first_name}!\n\n"
        f"💰 Coins: `{user['coins']}`\n"
        f"🎮 Games: `{user['stats']['games_played']}`",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command"""
    text = """🎮 *TokenArcade Commands*

/start - Main menu
/balance - Check coins
/daily - Get 50 coins
/help - This message
/mines 50 5 - Play mines
    """
    await update.message.reply_text(text, parse_mode='Markdown')

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check balance"""
    users = load_users()
    user = get_user(update.effective_user.id, users)
    level = (user['xp'] // 500) + 1
    
    text = (
        f"💰 *Your Balance*\n\n"
        f"Coins: `{user['coins']} ¢`\n"
        f"Level: `{level}`\n"
        f"XP: `{user['xp'] % 500}/500`\n"
        f"Games: `{user['stats']['games_played']}`"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

async def daily_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Daily bonus"""
    users = load_users()
    user = get_user(update.effective_user.id, users)
    today = datetime.now().date().isoformat()
    
    if user['stats']['last_daily'] == today:
        await update.message.reply_text("❌ Already claimed today!")
        return
    
    user['coins'] += 50
    user['stats']['last_daily'] = today
    save_users(users)
    
    await update.message.reply_text("✅ +50 coins!", parse_mode='Markdown')

async def mines_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Play Mines"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: `/mines 50 5`", parse_mode='Markdown')
        return
    
    try:
        bet = int(context.args[0])
        bombs = int(context.args[1])
    except ValueError:
        return
    
    users = load_users()
    user = get_user(update.effective_user.id, users)
    
    if bet > user['coins'] or bet < 1:
        await update.message.reply_text(f"❌ Invalid bet! You have {user['coins']}", parse_mode='Markdown')
        return
    
    if bombs not in [3, 5, 10]:
        await update.message.reply_text("❌ Bombs must be 3, 5, or 10!")
        return
    
    user['coins'] -= bet
    
    # Game logic
    safe_tiles = random.randint(1, min(8, 25 - bombs))
    mult = 1.0
    for i in range(safe_tiles):
        mult *= (25 - i) / (25 - i - bombs)
    mult *= 0.95
    
    hit_bomb = random.random() < (safe_tiles / (25 - bombs))
    
    if hit_bomb:
        result = f"💥 BOOM! Lost `{bet}`\nBalance: `{user['coins']}`"
    else:
        payout = int(bet * mult)
        user['coins'] += payout
        result = f"✅ Won `{payout}`! (Mult: `{mult:.2f}x`)\nBalance: `{user['coins']}`"
    
    user['stats']['games_played'] += 1
    user['stats']['total_wagered'] += bet
    user['xp'] += max(5, bet // 10)
    save_users(users)
    
    await update.message.reply_text(result, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    users = load_users()
    user = get_user(query.from_user.id, users)
    
    if query.data == 'balance':
        level = (user['xp'] // 500) + 1
        text = f"💰 Coins: `{user['coins']}`\nLevel: `{level}`"
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif query.data == 'profile':
        level = (user['xp'] // 500) + 1
        text = f"👤 *Profile*\n\nCoins: `{user['coins']}`\nLevel: `{level}`\nGames: `{user['stats']['games_played']}`"
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif query.data == 'dice_demo':
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        won = random.choice([True, False])
        payout = 10 if won else 0
        user['coins'] += payout
        user['stats']['games_played'] += 1
        save_users(users)
        await query.edit_message_text(
            f"🎲 {d1}+{d2}\n{'✅ Won 10' if won else '❌ Lost'}\nBalance: `{user['coins']}`",
            parse_mode='Markdown'
        )
    
    elif query.data == 'slots_demo':
        symbols = ['🍒', '🍋', '🍊', '🔔', '💎', '7️⃣']
        reels = [random.choice(symbols) for _ in range(3)]
        mult = 10 if reels[0] == reels[1] == reels[2] else (2 if reels[0] == reels[1] or reels[1] == reels[2] else 0)
        payout = 10 * mult
        user['coins'] += payout
        user['stats']['games_played'] += 1
        save_users(users)
        await query.edit_message_text(
            f"🎰 {''.join(reels)}\n{'✅ Won ' + str(payout) if payout else '❌ No match'}\nBalance: `{user['coins']}`",
            parse_mode='Markdown'
        )
    
    elif query.data == 'mines_info':
        await query.edit_message_text("💣 *Mines*\n\nUsage: `/mines 50 5`", parse_mode='Markdown')
    
    elif query.data == 'leaderboard':
        sorted_users = sorted(users.items(), key=lambda x: x[1]['coins'], reverse=True)[:5]
        text = "🏆 *Top 5*\n\n"
        for i, (uid, u) in enumerate(sorted_users, 1):
            text += f"{i}. User{uid[:3]} - `{u['coins']}`\n"
        await query.edit_message_text(text, parse_mode='Markdown')

# ===================== INITIALIZATION =====================

async def init_bot_app() -> Application:
    """Initialize the Telegram bot application"""
    global bot_app
    
    logger.info("🔧 Initializing Telegram Application...")
    
    bot_app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_cmd))
    bot_app.add_handler(CommandHandler("balance", balance_cmd))
    bot_app.add_handler(CommandHandler("daily", daily_cmd))
    bot_app.add_handler(CommandHandler("mines", mines_cmd))
    bot_app.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("✅ Telegram Application initialized successfully")
    
    return bot_app

# ===================== FLASK ROUTES =====================

@flask_app.route('/', methods=['GET'])
def index():
    """Health check"""
    return '✅ TokenArcade Bot is running', 200

@flask_app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle Telegram webhook"""
    global bot_app
    
    try:
        # Initialize bot on first request
        if bot_app is None:
            await init_bot_app()
        
        # Get update
        data = request.get_json()
        update = Update.de_json(data, bot_app.bot)
        
        # Process update
        await bot_app.process_update(update)
        
        return '', 204  # No content response
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return '', 500

# ===================== STARTUP =====================

async def on_startup():
    """Run on application startup"""
    global bot_app
    
    if bot_app is None:
        await init_bot_app()
    
    # Set webhook with Telegram
    try:
        await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        logger.info(f"✅ Webhook set to {WEBHOOK_URL}/webhook")
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")

# ===================== ASGI WRAPPER =====================

@flask_app.before_request
def before_request():
    """Initialize on first request"""
    if flask_app.config.get('startup_done') is None:
        asyncio.run(on_startup())
        flask_app.config['startup_done'] = True

# ===================== MAIN =====================

if __name__ == '__main__':
    logger.info(f"🚀 Starting TokenArcade Bot on port {PORT}")
    logger.info(f"📱 Webhook: {WEBHOOK_URL}/webhook")
    
    flask_app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False,
        use_reloader=False
    )
