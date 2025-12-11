from config import settings
from google.genai import types
from pydantic import BaseModel

class food_items(BaseModel):
    name : str
    description : str
    information : str

def recommend_food(food_json):
    try:
        prompt = f"""
        Based on the following food items, provide a healthy food recommendation:
        {food_json}
"""
        
        response = settings.CLIENT.models.generate_content(
            model=settings.MODEL,
            contents=[
                 prompt
            ],
            config={
                "system_instruction": "You are a nutrition expert. Provide healthy food recommendations based on the input.",
                "response_mime_type": "application/json",
                "response_schema": list[food_items],  # Define the schema for the response
            },
        )
        print("Response from Gemini:", response.text)
        return {"result": response.text}
    except Exception as e:
        print("Error in recommend_food:", str(e))
        return None