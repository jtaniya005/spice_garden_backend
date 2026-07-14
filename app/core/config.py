from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Spice Garden API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Groq
    GROQ_API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://your-frontend.onrender.com",
    ]

    class Config:
        env_file = ".env"

settings = Settings()