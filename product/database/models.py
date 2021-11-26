from .mongo_connection import MongoConnection
from product.module.kowsar_getter import KowsarGetter
from product.module.attributes import Attributes


class Product:
    def __init__(self):
        pass

    @staticmethod
    def create_product(system_code: str, specification: dict):
        system_code_generator = KowsarGetter()
        system_code_generator.product_getter()
        data = system_code_generator.system_code_name_getter(system_code)  # get data from system code
        req = dict()
        req['system_code'] = system_code
        req['config'] = data.get('config')
        req['model'] = data.get('model')
        req['brand'] = data.get('brand')
        req['sub_category'] = data.get('sub_category')
        req['main_category'] = data.get('main_category')
        attributes = Attributes()
        attrs = attributes.get_attributes(system_code)
        for x in attrs:
            if x.get('category') == 'model':
                req[x.get('name')] = specification.get(x.get('name'))
        with MongoConnection() as client:
            client.collection.insert_one(req)
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
