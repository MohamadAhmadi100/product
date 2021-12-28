from product.database.mongo_connection import MongoConnection
from product.module.attribute_api import Attribute
import json
import re

'''
{
  "name": "image-product",
  "label": "image",
  "input_type": 0,
  "required": false,
  "use_in_filter": false,
  "use_for_sort": false,
  "parent": "1001",
  "default_value": "/src/default.png",
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
    def get_attributes():
        return Attribute.get_all_attributes_by_assignee()

    @staticmethod
    def set_attribute_by_set_to_nodes():
        with MongoConnection() as client:
            client.attribute_kowsar_collection.remove()
            attrs = Attribute.get_all_attributes_by_assignee()
            kowsar = client.kowsar_collection.find({}, {'_id': 0, 'system_code': 1})
            kowsar_list = list(kowsar)
            client.attribute_kowsar_collection.insert_many(kowsar_list)
            for attr in attrs:
                if attr.get('set_to_nodes'):
                    client.attribute_kowsar_collection.update_many({'system_code': {'$regex': '^' + attr.get('parent')}}
                                                                   , {'$push': {'attributes': attr}},
                                                                   upsert=True)
                else:
                    client.attribute_kowsar_collection.update_one({'system_code': attr.get('parent')}, {# refactor
                        '$push': {'attributes': attr}}, upsert=True)
            data = client.attribute_kowsar_collection.find({}, {'_id': 0})
            return data
