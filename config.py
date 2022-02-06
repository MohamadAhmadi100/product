

class Settings:
    APP_NAME: str = "product"

    MONGO_HOST: str = "200.100.100.223"
    MONGO_PORT: int = 27017
    MONGO_USER: str = "root"
    MONGO_PASS: str = "qweasdQWEASD"

    REDIS_HOST: str = "200.100.100.223"
    REDIS_PORT: int = 6379
    REDIS_USER: str = ""
    REDIS_PASS: str = ""
    REDIS_DB: int = 1

    RABBIT_HOST: str = "200.100.100.205"

    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000

    TELEGRAM_BOT_TOKEN: str = "5010568783:AAH0ArPhZ_UtUFb-tUVAkPkQQLiRCHtflgM"
    CHAT_IDS: list = [172110099]


settings = Settings()
