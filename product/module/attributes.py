from product.database.mongo_connection import MongoConnection

'''
{
  "name": "image-product",
  "label": "image",
  "input_type": 0,
  "required": false,
  "use_in_filter": false,
  "use_for_sort": false,
  "parent": "1001",
  "default_value": [
    "/src/default.png"
  ],
  "values": [
    "string"
  ],
  "set_to_nodes": true,
  "assignee": [
    "product"
  ]
}
'''


class Attributes:
    @staticmethod
    def get_attributes(system_code):
        with MongoConnection() as client:
            data = client.kowsar_collection.find_one({'system_code': system_code}, {"attributes": 1, "_id": 0})
            return data

    @staticmethod
    def set_attributes(category, name, d_type, is_required, default_value, values, set_to_nodes):
        with MongoConnection() as client:
            # TODO: Serializers
            if set_to_nodes:
                re = '^' + category
                client.kowsar_collection.update_many({'system_code': {'$regex': re}}, {
                    '$set': {'attributes.' + name: {'name': name, 'd_type': d_type, 'is_required': is_required,
                                                    'default_value': default_value, 'values': values}}})
            else:
                client.kowsar_collection.update_one({'system_code': category}, {
                    '$set': {'attributes.' + name: {name: {'name': name, 'd_type': d_type, 'is_required': is_required,
                                                           'default_value': default_value, 'values': values}}}})

    @staticmethod
    def delete_attributes(category, name, delete_from_nodes):
        with MongoConnection() as client:
            if delete_from_nodes:
                re = '^' + category
                client.kowsar_collection.update_many({'system_code': {'$regex': re}},
                                                     {'$unset': {'attributes.' + name: 1}})
            else:
                client.kowsar_collection.update_one({'system_code': category},
                                                    {'$unset ': {'attributes.' + name: 1}})

    @staticmethod
    def update_attributes(category, old_name, new_name):
        with MongoConnection() as client:
            client.kowsar_collection.update_one({'system_code': category},
                                                {'$set': {
                                                    'attributes.' + old_name + '.name': new_name}})
            client.kowsar_collection.update_one({'system_code': category},
                                                {'$rename': {'attributes.' + old_name: 'attributes.' + new_name}})
