# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Twilio Settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str
    
    # Supabase Settings
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # OpenAI Settings (for future NLP)
    OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True  # Important for environment variables
        
settings = Settings()