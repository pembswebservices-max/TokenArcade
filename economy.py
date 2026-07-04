def add_xp(u, amt):
    u["xp"] += amt
    u["level"] = (u["xp"] // 250) + 1


def reward(u, bet, mult):
    payout = int(bet * mult)
    u["coins"] += payout
    u["weekly"] += payout
    u["season"] += payout // 10
    return payout
