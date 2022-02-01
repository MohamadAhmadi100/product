from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Product App"

    MONGO_HOST: str = "mongodb://localhost"
    MONGO_PORT: int = 27017
    MONGO_USER: str = ""
    MONGO_PASS: str = ""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_USER: str = ""
    REDIS_PASS: str = ""
    REDIS_DB: int = 1

    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000

    TELEGRAM_BOT_TOKEN: str = "5010568783:AAH0ArPhZ_UtUFb-tUVAkPkQQLiRCHtflgM"
    CHAT_IDS: list = [172110099]


settings = Settings()
