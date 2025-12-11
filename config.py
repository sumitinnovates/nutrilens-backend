import os
from dotenv import load_dotenv
from google import genai
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_KEY")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    MODEL = None
    CLIENT = None

    def __init__(self):
        self.CLIENT = genai.Client(api_key=self.GEMINI_API_KEY)
        self.MODEL = "gemini-2.5-flash"
    
    def apply_cors(self, app):
        """Attach CORS middleware to FastAPI app."""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.ALLOWED_ORIGINS,  # Or use a list of domains for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

settings = Settings()