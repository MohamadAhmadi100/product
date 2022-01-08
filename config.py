from pydantic import BaseSettings


class Settings(BaseSettings):
    MONGO_HOST = "mongodb://localhost"
    MONGO_PORT = 27017
    MONGO_USER = ""
    MONGO_PASS = ""

    UVICORN_HOST = "0.0.0.0"
    UVICORN_PORT = 8000


settings = Settings()