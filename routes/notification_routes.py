from fastapi import APIRouter, Body, Depends
from db import Notification, User,auth
from helpers import send_push_notification


router = APIRouter()

@router.post("/")
def create_notification(
    user_id: str = Body(...),
    title: str = Body(...),
    message: str = Body(...),
    seen: bool = Body(default=False)
):
    # Create a notification for the user
    result = Notification.create(user_id, title, message, seen)

    #send push notification 
    user = User.get_by_id(user_id)
    token = user['data'].get('fcm_token')
    if token:
        send_push_notification(token, title, message)

    return result

@router.get("/user/{user_id}")
def get_user_notifications(user_id: str):
    return Notification.get_by_user(user_id)

@router.patch("/{notification_id}/seen")
def mark_notification_seen(notification_id: str):
    return Notification.mark_as_seen(notification_id)

@router.delete("/{notification_id}")
def delete_notification(notification_id: str):
    return Notification.delete(notification_id)

@router.delete("/deleteAll")
def delete_All_scans(notification_id : list , user=Depends(auth.get_current_user)):
    try:
        scan = Notification.deleteMany(notification_id)
        if scan :
            return { "status": "success" , "message":"Deleted"}
        return {"status": "faild", "message":"failed to delete"}
    except Exception as e:
        return {"status": "error", "message": e}