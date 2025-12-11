from fastapi import APIRouter, Body, Depends
from db import User, auth

router = APIRouter()

#Auth signup insert the user in auth of supabase and then in our db
@router.post("/signup")
def sign_up(name: str = Body(...), email: str = Body(...), password: str = Body(...)):
    # print("Sign up called with name:", name, "email:", email, "password:", password)
    try:
        response = auth.user_sign_up_withEmail(name, email, password)
        if not "access_toeken" in response:
            User.create(response["user"]["id"], name, email, password)
            return {
                "message": response["message"],
                "user": response["user"]
            }
        return response
    except Exception as e:
        print("Error during sign up:", e)
        return {
            "message": "Error during sign up",
            "error": str(e)
        }

#Auth login the user and send the user id , email and access token which is JWT
@router.post("/login")
def login(email: str = Body(...), password: str = Body(...)):
    return auth.user_sign_in_withEmail(email, password)
    

#OAuth Google login is pending 
@router.get("/google-login")
def google_login():
    return auth.user_sign_in_withGoogle()

# Get_user will fetch the user by id
@router.get("/{user_id}")
def get_user(user_id: str):
    return User.get_by_id(user_id)

# Delete user by id from the database
@router.delete("/{user_id}")
def delete_user(user_id: str):
    return User.delete(user_id)


@router.post("/forgot-password")
def forgot_password(email: str = Body(...,embed=True)):
    return auth.user_ResetPassword(email)

@router.post("/reset-password")
def reset_password(new_password: str = Body(...), user = Depends(auth.get_current_user)):
    return auth.user_reset(new_password)