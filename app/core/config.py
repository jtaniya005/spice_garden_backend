from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "Spice Garden API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Groq
    GROQ_API_KEY: str = ""
    USE_LIVE_CHAT: bool = True

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://your-frontend.onrender.com",
    ]

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()