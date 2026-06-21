import os
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client["yfgame"]
collection = db["points"]

def get_points(user_id: int) -> dict:
    doc = collection.find_one({"user_id": user_id})
    if not doc:
        return {"solo": 0, "group": 0}
    return {"solo": doc.get("solo", 0), "group": doc.get("group", 0)}

def add_solo_points(user_id: int, amount: int = 1):
    collection.update_one(
        {"user_id": user_id},
        {"$inc": {"solo": amount}},
        upsert=True
    )

def add_group_points(user_id: int, amount: int = 1):
    collection.update_one(
        {"user_id": user_id},
        {"$inc": {"group": amount}},
        upsert=True
    )

def transfer_points(from_id: int, to_id: int, amount: int) -> bool:
    from_pts = get_points(from_id)
    total = from_pts["solo"] + from_pts["group"]
    if total < amount:
        return False
    solo = from_pts["solo"]
    if solo >= amount:
        collection.update_one({"user_id": from_id}, {"$inc": {"solo": -amount}}, upsert=True)
    else:
        remaining = amount - solo
        collection.update_one({"user_id": from_id}, {"$set": {"solo": 0}, "$inc": {"group": -remaining}}, upsert=True)
    collection.update_one({"user_id": to_id}, {"$inc": {"solo": amount}}, upsert=True)
    return True
