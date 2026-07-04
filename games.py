import random
from economy import reward, add_xp
from storage import get, save
from ui import home_kb

feed = []

def add_feed(msg):
    feed.append(msg)
    if len(feed) > 20:
        feed.pop(0)

async def dice(update, context):
    u = get(update.effective_user.id)

    msg = await context.bot.send_dice(update.effective_chat.id, "🎲")
    bet = 100
    u["coins"] -= bet

    mult = 2.5 if msg.dice.value == 6 else 1.9 if msg.dice.value >= 4 else 0
    payout = reward(u, bet, mult)

    add_xp(u, 10)
    add_feed(f"🎲 {payout}")

    save()


async def darts(update, context):
    u = get(update.effective_user.id)
    msg = await context.bot.send_dice(update.effective_chat.id, "🎯")

    bet = 100
    u["coins"] -= bet

    mult = 2 if msg.dice.value >= 5 else 0
    reward(u, bet, mult)

    save()


async def basket(update, context):
    u = get(update.effective_user.id)
    msg = await context.bot.send_dice(update.effective_chat.id, "🏀")

    bet = 100
    u["coins"] -= bet

    reward(u, bet, 2 if msg.dice.value >= 4 else 0)

    save()


async def bowling(update, context):
    u = get(update.effective_user.id)
    msg = await context.bot.send_dice(update.effective_chat.id, "🎳")

    bet = 100
    u["coins"] -= bet

    reward(u, bet, 2 if msg.dice.value >= 4 else 0)

    save()


async def football(update, context):
    u = get(update.effective_user.id)
    msg = await context.bot.send_dice(update.effective_chat.id, "⚽")

    bet = 100
    u["coins"] -= bet

    reward(u, bet, 2 if msg.dice.value in [4,5] else 0)

    save()
