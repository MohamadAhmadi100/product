import requests
import pymongo
from fastapi.testclient import TestClient

from app.main import app
from config import settings

client = TestClient(app)


class TestConnection:
    def test_internet_on(self):
        assert requests.get('http://www.google.com').status_code == 200

    def test_uvicorn_server_up(self):
        assert client.get("/api/v1/docs").status_code == 200

    def test_mongo_server_up(self):
        try:
            mongo = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT,
                                        username=settings.MONGO_USER, password=settings.MONGO_PASS)
            mongo.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            assert False