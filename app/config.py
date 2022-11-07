import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Settings
    APP_NAME = os.getenv("APP_NAME")

    # Mongo DB
    MONGO_HOST: str = os.getenv("MONGO_HOST")
    MONGO_PORT: int = int(os.getenv("MONGO_PORT"))
    MONGO_USER: str = os.getenv("MONGO_USER")
    MONGO_PASS: str = os.getenv("MONGO_PASS")

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
    REDIS_USER: str = os.getenv("REDIS_USER")
    REDIS_PASS: str = os.getenv("REDIS_PASS")
    REDIS_DB: int = int(os.getenv("REDIS_DB"))

    # RabbitMQ
    RABBIT_HOST: str = os.getenv("RABBIT_HOST")
    RABBIT_PORT: int = int(os.getenv("RABBIT_PORT"))
    RABBIT_USER: int = os.getenv("RABBIT_USER")
    RABBIT_PASS: int = os.getenv("RABBIT_PASS")

    # Kavenegar
    TOKEN: str = os.getenv("TOKEN")
    SENDER: str = os.getenv("SENDER")
    RECIPIENTS: list = os.getenv("RECIPIENTS")
    TEMPLATE: str = os.getenv("TEMPLATE")

    # telegram
    TELEGRAM_REQUEST_URL: str = os.getenv("TELEGRAM_REQUEST_URL")
    TELEGRAM_ID: list = os.getenv("TELEGRAM_ID")
    DEBUG_MODE: bool = int(os.getenv("DEBUG_MODE"))


settings = Settings()
