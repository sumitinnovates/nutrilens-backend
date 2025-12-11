from supabase import create_client, Client
from config import settings
from fastapi import Header, HTTPException
from PIL import Image
import io
import requests

class Database:
    #Connecting to Supabase on Instance of Database Class 
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


    #Inter One record into a Table
    def insertOne(self,table:str, **kargs):
        try:
            if table and kargs :
                # print("Table : ",table,"Data : ",kargs)
                response = (
                    self.client.table(table).insert(kargs).execute()
                )
                return {"status": 200,"message": "Successfully inserted", "data": response.data}
            else:
                return{"status": 404, "message": "Table or data not provided"}
        except Exception as e:
            print("Error in insertOne DB : ",e)
            return {"status": 500, "message": "Error inserting data", "error": str(e)}

    #Select single record from specific table through specific column and value
    def findOne(self, table:str, **kagrs):
        try:

            if table and kagrs : 
                key ,value = next(iter(kagrs.items()))
                print("Key : ",key,"Value : ",value)
            
                response = (
                    self.client.table(table).select("*").eq(key,value).execute()
                )

                if response.data:
                    return {
                        "Status": 200,
                        "message": "Successfully fetched data",
                        "data": response.data[0]
                    }
                else:
                    return {"Status":404}
        except Exception as e:
            print("Error : ",e)
            return {"Status":500}

    #Select Multiple records from specific Table  
    def findMany(self,table:str):
        if table:
            try:
                response = (
                    self.client.table(table).select("*").execute()
                )
                if response.data:
                    return {
                        "status": 200,
                        "message": "Successfully fetched data",
                        "data": response.data
                    }
                else:
                    return {
                        "status": 404,
                        "message": "No data found"
                    }
            except Exception as e:
                print("Error : ",e)

    #Select multiple records of specific user from specific Table
    def findMany_of_User(self,table:str,token:str):
        try:
            if table and token :
                response= (
                    self.client.table(table).select("*").eq("user_id",token).execute()
                )
                if response:
                    return {
                        "status": 200,
                        "message": "Successfully fetched data",
                        "data": response.data
                    }
                else:
                    return{
                        "status": 404,
                        "message": "No data found"
                    }
            else:
                print("Provide a proper table and token")
                return 
        except Exception as e:
            print("Error : ",e)
            return {
                "status": 500,
                "message": "Error fetching data",
                "error": str(e)
            }

    #Insert Multiple records into a specific Table (use it for insert dummy data into a specific Table)       
    def insertMany(self, table:str,data:list):
        try:
            if table and data:  
                response = (
                    self.client.table(table).insert(data).execute()
                )
                if response:
                    return {
                        "status": 200,
                        "message": "Successfully Inserted",
                        "data": response.data
                    }
        except Exception as e:
            print("Error : ",e)
            return {
                "status": 500,
                "message": "Error inserting data",
                "error": str(e)
            }

    #Update the single record of a specific Table 
    def updateOne(self,table:str,column:str,ID_key:str,**kargs):
        if table and column and ID_key and kargs:
            key,value = next(iter(kargs.items()))
            if key and value:
                try:
                    response = (
                        self.client.table(table).update({key:value}).eq(column,ID_key).execute()
                    )
                    if response:
                        return {
                            "status": 200,
                            "message": "Successfully Updated",
                            "data": response.data
                        }
                except Exception as e:
                    print("Error : ",e)
                    return {
                        "status": 500,
                        "message": "Error updating data",
                        "error": str(e)
                    }

    #Update the multiple records of a specific Table
    def updateMany(self,table:str,column:str,ID_key:str,**kargs):
        if table and column and ID_key and kargs:
            try:
                count = 0
                for key,value in kargs.items():
                    response = (
                        self.client.table(table).update({key : value}).eq(column,ID_key).execute()
                    )
                    if response:
                        count += 1
                
                if count == len(kargs):
                    return {
                        "status": 200,
                        "message": "Successfully Updated",
                        "data": response.data
                    }

            except Exception as e:
                print("Error : ",e)  
                return {
                    "status": 500,
                    "message": "Error updating data",
                    "error": str(e)
                } 
    
    #Delete one record from a specific Table
    def deleteOne(self,table:str,column:str,ID_key:str):
        if table and column and ID_key:
            try:
                response = (
                    self.client.table(table).delete().eq(column,ID_key).execute()
                )
                if response:
                    return {"status": 200 , "message": "Successfully deleted"}
            except Exception as e:
                print("Error : ",e)
                return {"status": 500, "message": "Error deleting data", "error": str(e)}

    #Delete multiple records from a specific Table    
    def deleteMany(self,table:str,column:str,ID_keys:list):
        if table and column and ID_keys:
            try:
                response =(
                    self.client.table(table).delete().in_(column,ID_keys).execute()
                )
                if response:
                    return {"status": 200, "message": "Successfully deleted"}
            except Exception as e:
                print("Error : ",e)
                return {"status": 500, "message": "Error deleting data", "error": str(e)}

#Auth Class  
class Auth(Database):

    def __init__(self):
        super().__init__()
        self.auth = self.client.auth

    def user_sign_out(self):
        response = self.auth.sign_out() 

    def user_sign_up_withEmail(self,name:str,email:str,password:str):
        if email and password :
            try:
                response = self.auth.sign_up(
                    {
                        "email" : email,
                        "password" : password,
                    }
                )
                # print("Response on signup : ",response)
                user_id = response.user.id
                user_email = response.user.email

                if not response.session:
                    return {
                        "message": "User created. Please verify your email before logging in.",
                        "user": {
                        "id": user_id,
                        "email": user_email
                        },
                    }
                
                return {
                    "message": "User created and logged in successfully.",
                        "user": {
                            "id": response.user.id,
                            "email": email,
                            "name": name
                        },
                        "access_token": response.session.access_token
                    }
                
            except Exception as e:
                print("Error in sign_up : ",e)
                return {
                    "status": 500,
                    "message": str(e),
                }
    
    def user_sign_in_withEmail(self,email:str,password:str):
        if email and password :
            try:
                response = self.auth.sign_in_with_password(
                    {
                        "email":email,
                        "password":password,
                    }
                )
                if response :
                #    print("Response on login : ",response)
                   return {
                        "user": {
                            "id": response.user.id,
                            "email": email
                        },
                        "access_token": response.session.access_token
                    }
            except Exception as e :
                print("Error in sign_in : ",e)
                return { 
                    "status": 500,
                    "message": str(e),
                }

    def user_sign_in_withGoogle(self):
        try:
            response = self.auth.sign_in_with_oauth({"provider": "google"})
            if response:
                user_id = response.user.id
                user_email = response.user.email
                user_name = response.user.user_metadata.get("full_name") or response.user.user_metadata.get("name")

                #lazy import to avoid circular dependency
                from models import User

                User_exists = User.create_if_not_exists(user_id, user_name, user_email)
                if User_exists:
                    return {
                        "user": {
                            "id": user_id,
                            "email": user_email,
                            "name": user_name
                        },
                        "access_token": response.session.access_token
                    }
        except Exception as e:
            print("Error during Google sign-in:", e)
            return {
                "status": 500,
                "message": str(e),
            }
    
    def user_reset(self,**kagrs):
        key , value = next(iter(kagrs.items()))
        try:
            if key == "email":
                response = self.auth.update_user(
                    {key : value}
                )
                if response:
                    return {
                        "message": "User email updated successfully",
                        "user": {
                            "id": response.user.id,
                            "email": value
                        }
                    }
            if key == "password":
                response = self.auth.update_user(
                    {key, value}
                )
                if response:
                    return {
                        "message": "User password updated successfully",
                        "user": {
                            "id": response.user.id,
                            "email": response.user.email
                        }
                    }
        except Exception as e:
            print("Error in user_reset: ",e)  
            return {
                "status": 500,
                "message": str(e),
            } 

    def user_ResetPassword(self,email:str):
        try:
            url = f"{settings.SUPABASE_URL}/auth/v1/recover"
            headers = {
                "apikey": settings.SUPABASE_KEY,
                "Content-Type": "application/json"
            }
            payload = {"email": email}

            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                print("Password reset email sent!")
            else:
                print("Error:", response.json())
        except Exception as e:
            print("Error : ",e)
            return {
                "status": 500,
                "message": str(e),
            }
    
    # Get the current user based on the token
    def get_current_user(self, authorization: str = Header(...)):
        try:
            token = authorization.replace("Bearer ", "")
            user = self.auth.get_user(token)
            return user
        except Exception as e:
            print("Error fetching current user:", e)
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Refresh the session using a refresh token
    def refresh_session(self, refresh_token: str):
        try:
            return self.auth.refresh_session(refresh_token)
        except Exception as e:
            print("Error refreshing session:", e)
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


class Storage(Database):
    __ImageBucket = "food-images"
    def __init__(self):
        super().__init__()
        self.storage = self.client.storage

    # Compress an image to a target size in 90 KB
    def compress_image_to_target_size(self, image_data: bytes, target_kb=90, min_quality=20) -> bytes:
        image = Image.open(io.BytesIO(image_data))
        quality = 95
        step = 5
        while quality >= min_quality:
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', optimize=True, quality=quality)
            size_kb = buffer.tell() / 1024
            if size_kb <= target_kb:
                return buffer.getvalue()
            quality -= step
        return buffer.getvalue() 

    def upload_file(self, image, image_name: str):
        try:
            if image:
                file_name = f"uploads/{image_name}"
                compressed_image = self.compress_image_to_target_size(image)
                # Upload the file to the specified bucket
                response = self.storage.from_(self.__ImageBucket).upload(file_name, compressed_image)
                public_url = self.storage.from_(self.__ImageBucket).get_public_url(file_name)
                
                if response:
                    return {
                        "status": 200,
                        "message": "File uploaded successfully",
                        "file_name": file_name,
                        "public_url": public_url
                    }
            else:
                return {"status": 400, "message": "No file provided"}
        except Exception as e:
            print("Error uploading file:", e)
            return {"status": 500, "message": str(e)}


db = Database()
auth = Auth()
storage = Storage()






