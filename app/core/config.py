from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Spice Garden API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Ollama
    OLLAMA_URL: str = "http://localhost:11434/api/chat"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_TIMEOUT: int = 60

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"

settings = Settings()
