import sys

sys.path.append("..")

from source.mongo_connection import MongoConnection
from source.kowsar_getter import KowsarGetter


class Product:
    def __init__(self):
        pass

    @staticmethod
    def create_product(system_code: str):
        system_code_generator = KowsarGetter()
        system_code_generator.product_getter()
        data = system_code_generator.system_code_name_getter(system_code)  # get data from system code
        data = {
            "system_code": system_code,
            "config": data.get("config", None),
            "model": data.get("model", None),
            "brand": data.get("brand", None),
            "sub_category": data.get("sub_category", None),
            "main_category": data.get("main_category", None)
        }
        with MongoConnection() as client:
            client.collection.insert_one(data)
        return system_code

    @staticmethod
    def get_product(system_code: str):
        pipe_line = {
            "system_code": system_code
        }
        with MongoConnection() as client:
            data = client.collection.find_one(pipe_line, {"_id": 0})
        return data

    @staticmethod
    def get_all_products(page: int, product_count: int = 3):  # product_count is the number of products per page
        skip = product_count * (page - 1)
        if skip >= 0:
            with MongoConnection() as client:
                data = client.collection.find({}, {"_id": 0}).limit(product_count).skip(skip)
            products = [product for product in data]
            return products
        return []

    @staticmethod
    def delete_product(system_code: str):
        pip_line = {
            "system_code": system_code
        }
        with MongoConnection() as client:
            client.collection.delete_one(pip_line)
