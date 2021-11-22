import os

import requests
from dotenv import load_dotenv


class TestConnection:
    def test_internet_on(self):
        assert requests.get('http://www.google.com').status_code == 200

    def test_uvicorn_server_up(self):
        load_dotenv()
        address = os.getenv("UVICORN_HOST") + ":" + os.getenv("UVICORN_PORT") + "/docs"
        assert requests.get(address).status_code == 200

    def test_mongo_server_up(self):
        load_dotenv()
        address = os.getenv("MONGO_HOST") + ":" + os.getenv("MONGO_PORT") + "/"
        assert requests.get(address).status_code == 200
