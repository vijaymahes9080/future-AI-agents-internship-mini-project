import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "EWB Student Record Management System"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./students.db")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "10.0"))
    MAX_PAGE_SIZE: int = 100
    DEFAULT_PAGE_SIZE: int = 10

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
