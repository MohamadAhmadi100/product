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
        data = system_code_generator.config_code_getter(system_code)
        config = data.get("config", None)
        model = data.get("model", None)
        brand = data.get("brand", None)
        sub_category = data.get("sub_category", None)
        main_category = data.get("main_category", None)
        data = {
            "system_code": system_code,
            "config": config,
            "model": model,
            "brand": brand,
            "sub_category": sub_category,
            "main_category": main_category
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
    def get_all_products(page: int, product_count: int = 3):
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
