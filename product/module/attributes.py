from product.database.mongo_connection import MongoConnection


class Attributes:
    @staticmethod
    def get_attributes(system_code):
        with MongoConnection() as client:
            data = client.kowsar_collection.find_one({'system_code': system_code}, {"attributes": 1, "_id": 0})
            return data

    @staticmethod
    def set_attributes(category, name, d_type, is_required, default_value, values, set_to_nodes):
        with MongoConnection() as client:
            # check name for unique one
            if set_to_nodes:
                re = '^' + category
                client.kowsar_collection.update_many({'system_code': {'$regex': re}}, {
                    '$push': {'attributes': {'name': name, 'd_type': d_type, 'is_required': is_required,
                                             'default_value': default_value,
                                             'values': values}}})
            else:
                client.kowsar_collection.update_one({'system_code': category}, {
                    '$push': {'attributes': {'name': name, 'd_type': d_type, 'is_required': is_required,
                                             'default_value': default_value,
                                             'values': values}}})

    @staticmethod
    def delete_attributes(category, name, delete_from_nodes):
        with MongoConnection() as client:
            if delete_from_nodes:
                re = '^' + category
                client.kowsar_collection.update_many({'system_code': {'$regex': re}},
                                                     {'$pull': {'attributes.name': name}})
            else:
                client.kowsar_collection.update_one({'system_code': category},
                                                    {'$pull': {'attributes.name': name}})

    @staticmethod
    def update_attributes(category, old_name, new_name):
        with MongoConnection() as client:
            # check if it nodes has the same name
            re = '^' + category + '$'
            client.kowsar_collection.update_one({'system_code': {'$regex': re}},
                                                {'$rename': {'attributes.0.name': 'attributes.0.main'}})
