from .supabase_client import db
from fastapi import HTTPException
from uuid import UUID

class User:
    __table = "users"

    @classmethod
    def create(cls,id:str, name: str, email: str, password: str):
        return db.insertOne(cls.__table, id=id, name=name, email=email)

    @classmethod
    def get_by_id(cls, user_id: UUID):
        response= db.findOne(cls.__table, id=user_id)
        if response:
            return response
        elif response == {"Status": 404}:
            raise HTTPException(status_code=response.get("Status"), detail="User not found")

    @classmethod
    def get_all(cls):
        return db.findMany(cls.__table)

    @classmethod
    def update(cls, user_id: UUID, **data):
        return db.updateOne(cls.__table, "id", user_id, **data)

    @classmethod
    def delete(cls, user_id: UUID):
        return db.deleteOne(cls.__table, "id", user_id)
    
    @classmethod
    def create_if_not_exists(cls, user_id: UUID, name: str, email: str):
        existing = db.findOne(cls.__table, id=user_id)
        if not existing:
            return db.insertOne(cls.__table, id=user_id, name=name, email=email)
        return existing
    
    @classmethod
    def get_by_email(cls, email: str):
        return db.findOne(cls.__table, email=email)


class FoodScan:
    __table = "food_scans"

    @classmethod
    def create(cls, user_id: UUID, image_url: str, nutrients: dict):
        return db.insertOne(cls.__table, user_id=user_id, image_url=image_url, nutrition_json=nutrients)

    @classmethod
    def get_by_id(cls, scan_id: UUID):
        return db.findOne(cls.__table, id=scan_id)

    @classmethod
    def get_by_user(cls, user_id: UUID):
        return db.findMany_of_User(cls.__table, user_id)

    @classmethod
    def get_all(cls):
        return db.findMany(cls.__table)

    @classmethod
    def update(cls, scan_id: UUID, **data):
        return db.updateOne(cls.__table, "id", scan_id, **data)

    @classmethod
    def delete(cls, scan_id: UUID):
        return db.deleteOne(cls.__table, "id", scan_id)
    
    @classmethod
    def insert_many(cls, scans: list):
        return db.insertMany(cls.__table, scans)
    
    @classmethod
    def get_latest(cls, user_id: UUID):
        return db.client.__table(cls.__table).select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute().data[0]
    
    @classmethod
    def deleteMany(cls,scan_id : list):
        return db.deleteMany(cls.__table,"id",scan_id)


class Notification:
    __table = "notifications"

    @classmethod
    def create(cls, user_id: UUID, title: str, message: str, seen: bool = False):
        return db.insertOne(cls.__table, user_id=user_id, title=title, message=message, seen=seen)

    @classmethod
    def get_by_user(cls, user_id: UUID):
        return db.findMany_of_User(cls.__table, user_id)

    @classmethod
    def mark_as_seen(cls, notification_id: UUID):
        return db.updateOne(cls.__table, "id", notification_id, seen=True)

    @classmethod
    def delete(cls, notification_id: UUID):
        return db.deleteOne(cls.__table, "id", notification_id)
    
    @classmethod
    def mark_all_as_seen(cls, user_id: UUID):
        return db.updateMany(cls.__table, "user_id", user_id, seen=True)
    
    @classmethod
    def deleteMany(cls,notification_id : list):
        return db.deleteMany(cls.__table,"id",notification_id)
    
class Recommendation:
    __table = "recommendation"

    @classmethod
    def create(cls, user_id: UUID, food_id : UUID, recommendation: dict):
        return db.insertOne(cls.__table, user_id=user_id, food_id = food_id, recommend_json=recommendation)

    @classmethod
    def get_by_id(cls, scan_id: UUID):
        return db.findOne(cls.__table, id=scan_id)

    @classmethod
    def get_by_user(cls, user_id: UUID):
        return db.findMany_of_User(cls.__table, user_id)

    @classmethod
    def get_all(cls):
        return db.findMany(cls.__table)

    @classmethod
    def update(cls, scan_id: UUID, **data):
        return db.updateOne(cls.__table, "id", scan_id, **data)

    @classmethod
    def delete(cls, scan_id: UUID):
        return db.deleteOne(cls.__table, "id", scan_id)
    
    @classmethod
    def deleteMany(cls,recommendation_id : list):
        return db.deleteMany(cls.__table,"id",recommendation_id)