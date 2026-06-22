import os
import motor.motor_asyncio

MONGODB_URI = os.getenv("MONGODB_URI")

# عميل واحد فقط طوال عمر البوت - لا تفتح عميل جديد بكل استدعاء
_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
_db = _client["yfgame"]
_collection = _db["points"]


def get_collection():
    return _collection


async def get_points(user_id: int) -> dict:
    try:
        doc = await _collection.find_one({"user_id": user_id})
        if not doc:
            return {"solo": 0, "group": 0}
        return {"solo": doc.get("solo", 0), "group": doc.get("group", 0)}
    except Exception as e:
        print(f"⚠️ get_points error: {e}")
        return {"solo": 0, "group": 0}


async def add_solo_points(user_id: int, amount: int = 1):
    try:
        await _collection.update_one(
            {"user_id": user_id},
            {"$inc": {"solo": amount}},
            upsert=True
        )
    except Exception as e:
        print(f"⚠️ add_solo_points error: {e}")


async def add_group_points(user_id: int, amount: int = 1):
    try:
        await _collection.update_one(
            {"user_id": user_id},
            {"$inc": {"group": amount}},
            upsert=True
        )
    except Exception as e:
        print(f"⚠️ add_group_points error: {e}")


async def transfer_points(from_id: int, to_id: int, amount: int) -> bool:
    try:
        from_pts = await get_points(from_id)
        total = from_pts["solo"] + from_pts["group"]
        if total < amount:
            return False
        solo = from_pts["solo"]
        if solo >= amount:
            await _collection.update_one({"user_id": from_id}, {"$inc": {"solo": -amount}}, upsert=True)
        else:
            remaining = amount - solo
            await _collection.update_one({"user_id": from_id}, {"$set": {"solo": 0}, "$inc": {"group": -remaining}}, upsert=True)
        await _collection.update_one({"user_id": to_id}, {"$inc": {"solo": amount}}, upsert=True)
        return True
    except Exception as e:
        print(f"⚠️ transfer_points error: {e}")
        return False
