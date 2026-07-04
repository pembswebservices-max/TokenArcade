import json
from config import DATA_FILE

users = {}

def load():
    global users
    try:
        users = json.load(open(DATA_FILE))
    except:
        users = {}

def save():
    json.dump(users, open(DATA_FILE, "w"), indent=2)

def get(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "coins": 1000,
            "xp": 0,
            "level": 1,
            "weekly": 0,
            "season": 0,
            "streak": 0,
            "last_daily": None,
            "withdrawals": [],
            "deposits": []
        }
    return users[uid]
