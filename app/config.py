import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Settings
    APP_NAME = "product"

    # Mongo DB
    MONGO_HOST: str = "200.100.100.223"
    MONGO_PORT: int = 27017
    MONGO_USER: str = "root"
    MONGO_PASS: str = "qweasdQWEASD"

    # Redis
    REDIS_HOST: str = "200.100.100.223"
    REDIS_PORT: int = 6379
    REDIS_USER: str = ""
    REDIS_PASS: str = ""
    REDIS_DB: int = 1

    # RabbitMQ
    RABBIT_HOST: str = "200.100.100.208"
    RABBIT_PORT: int = 5672
    RABBIT_USER: int = "rbtmq"
    RABBIT_PASS: int = "rbtmq@RBTMQ"

    # Kavenegar
    TOKEN: str = "535041646375714D57613535695561696E7355724A796B2B5657715833434939"
    SENDER: str = "10008663"
    RECIPIENTS: list = ["09025606950", "09113485808", "09123854358"]
    TEMPLATE: str = "service-error"


settings = Settings()
