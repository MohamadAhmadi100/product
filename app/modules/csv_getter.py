import csv
import os

from app.helpers.mongo_connection import MongoConnection


def get_csv(storage_id):
    with MongoConnection() as client:
        result = client.product.aggregate([
            {
                '$project': {
                    'system_code': 1,
                    'keys': {
                        '$objectToArray': '$warehouse_details'
                    },
                    'root_obj': '$$ROOT'
                }
            }, {
                '$unwind': '$keys'
            }, {
                '$project': {
                    'system_code': 1,
                    'customer_type': '$keys.k',
                    'zz': {
                        '$objectToArray': '$keys.v.storages'
                    },
                    'root_obj': 1
                }
            }, {
                '$unwind': '$zz'
            }, {
                '$project': {
                    'system_code': 1,
                    'storage_id': '$zz.k',
                    'customer_type': 1,
                    'quantity': '$zz.v.quantity',
                    'reserved': '$zz.v.reserved',
                    'root_obj': 1
                }
            }, {
                '$match': {
                    'quantity': {
                        '$gt': 0
                    },
                    'storage_id': storage_id
                }
            }, {
                '$group': {
                    '_id': '$root_obj.system_code',
                    'fieldN': {
                        '$push': '$$ROOT'
                    },
                    'quantity': {
                        '$sum': '$quantity'
                    },
                    'reserved': {
                        '$sum': '$reserved'
                    }
                }
            }, {
                '$project': {
                    'fieldN': {
                        '$first': '$fieldN'
                    },
                    'quantity': 1,
                    'reserved': 1
                }
            }, {
                '$project': {
                    'system_code': '$_id',
                    '_id': 0,
                    'quantity': '$quantity',
                    'reserved': '$reserved',
                    'name': '$fieldN.root_obj.name',
                    'color': '$fieldN.root_obj.color',
                    'guaranty': '$fieldN.root_obj.guaranty'
                }
            }, {
                "$sort": {
                    "system_code": 1
                }
            }
        ])
        result = list(result)
        with open('Products.csv', 'w', encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["system_code", "name", "color", "guaranty", "quantity", "reserved"])
            for row in result:
                writer.writerow([row['system_code'], row['name'], row['color'], row['guaranty'],
                                 row.get('quantity'), row.get("reserved")])

        with open('Products.csv', 'rb') as f:
            data = f.read()
        os.remove('Products.csv')
        return data.decode("utf-8-sig")
