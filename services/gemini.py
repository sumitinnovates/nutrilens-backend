from config import settings
from google.genai import types
from pydantic import BaseModel


def analyze_image(image_bytes):
    try:
       
        class FoodItem(BaseModel):
            name: str
            calories: float
            fat_g: float
            carbs_g: float
            protein_g: float
            when_to_eat: str
            harmful_aspects: str
            how_much_to_eat: str
            summary: str


        prompt = (
            "Identify all food items in this image and return a JSON array, "
            "each object should have: name, calories, protein (g), fat (g), carbs (g). "
            "Also mention how it is harmful, how much to eat, and when to eat. "
            "Respond only in valid JSON format. Summarize this whole for the user."
        )

        client = settings.CLIENT
        response = client.models.generate_content(
            model=settings.MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),prompt],
                 config={
                    "response_mime_type": "application/json",
                    "response_schema": list[FoodItem],  # Tell Gemini to follow our schema
                },
        )

        return {"result": response.text}

    except Exception as e:
        print("Error in analyze_image:", str(e))
        return None