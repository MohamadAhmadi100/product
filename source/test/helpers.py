import os

import requests
from dotenv import load_dotenv


class Helpers:
    @staticmethod
    def get_url_json(postfix):
        load_dotenv()
        uvicorn_ip_address = os.getenv("UVICORN_HOST") + ':' + os.getenv("UVICORN_PORT")
        return requests.get(uvicorn_ip_address + postfix).json()

    @staticmethod
    def delete_method_json(postfix) -> None:
        load_dotenv()
        uvicorn_ip_address = os.getenv("UVICORN_HOST") + ':' + os.getenv("UVICORN_PORT")
        requests.delete(uvicorn_ip_address + postfix)

    @staticmethod
    def post_method_json(postfix, data):
        load_dotenv()
        uvicorn_ip_address = os.getenv("UVICORN_HOST") + ':' + os.getenv("UVICORN_PORT")
        response = requests.post(uvicorn_ip_address + postfix, data=data)
        return response
