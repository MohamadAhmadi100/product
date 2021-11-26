from product.database.mongo_connection import MongoConnection


class Attributes:
    @staticmethod
    def get_attributes(system_code):
        with MongoConnection() as client:
            attrs = client.attribute_collection.find({'system_code': system_code}, {"_id": 0})
            # attrs = [{'category': 'model', 'sub_category': '', 'name': 'image', 'type': 'str', 'is_required': 'True',
            #           'default_value': '/src/default.png', 'values': []},
            #          {'category': 'model', 'sub_category': '', 'name': 'price', 'type': 'int', 'is_required': 'True',
            #           'default_value': '0',
            #           'values': []}]
            return attrs
