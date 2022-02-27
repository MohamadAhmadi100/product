import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME")

    MONGO_HOST: str = os.getenv("MONGO_HOST")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT"))
    MONGO_USER: str = os.getenv("MONGO_USER")
    MONGO_PASS: str = os.getenv("MONGO_PASS")

    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    REDIS_USER: str = os.getenv("REDIS_USER")
    REDIS_PASS: str = os.getenv("REDIS_PASS")
    REDIS_DB: int = int(os.getenv("REDIS_DB"))

    RABBIT_HOST: str = os.getenv("RABBIT_HOST")

    UVICORN_HOST: str = os.getenv("UVICORN_HOST")
    UVICORN_PORT: int = int(os.getenv("UVICORN_PORT"))

    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_IDS: list = [int(chat_id) for chat_id in os.getenv("CHAT_IDS").split(",")]


settings = Settings()
