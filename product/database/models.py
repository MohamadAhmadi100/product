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
        req_list = ['config', 'model', 'brand', 'sub_category', 'main_category']
        for i in req_list:
            req[i] = data.get(i)
        with MongoConnection() as client:
            attrs = client.attribute_kowsar_collection.find({}, {'_id': 0})
            for attr in attrs:
                if attr.get('system_code') == system_code:
                    if attr.get('attributes'):
                        for i in attr.get('attributes'):
                            for k, v in specification.items():
                                if i.get('name') == k:
                                    req[i.get('name')] = v
            if client.collection.find_one({'system_code': system_code}):
                return {'error': 'system_code already exists'}
            client.collection.insert_one(req)
            return system_code

    @staticmethod
    def update_product(system_code: str, specification: dict):
        with MongoConnection() as client:
            if client.collection.find_one({'system_code': system_code}):
                client.collection.update_one({'system_code': system_code}, {'$set': specification})
                return {'messages': 'product updated'}
            return {'error': 'system_code does not exist'}

    @staticmethod
    def get_all_attribute_by_system_code(system_code: str):
        with MongoConnection() as client:
            attrs = client.attribute_kowsar_collection.find_one({'system_code': system_code}, {'_id': 0})
            return [i.get('name') for i in attrs.get('attributes')]

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


class Assignees:
    @staticmethod
    def get_all_attributes_from_attribute_api():
        return Attributes.get_attributes()

    @staticmethod
    def set_all_attributes_by_set_to_nodes():
        return Attributes.set_attribute_by_set_to_nodes()