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
                    'customer_type': 'B2B',
                    'quantity': {
                        '$gt': 0
                    }
                }
            }, {
                '$group': {
                    '_id': '$storage_id',
                    'products': {
                        '$push': {
                            'system_code': '$system_code',
                            'storage_id': '$storage_id',
                            'quantity': '$quantity',
                            'reserved': '$reserved',
                            'name': '$root_obj.name',
                            'color': '$root_obj.color',
                            'guaranty': '$root_obj.guaranty'
                        }
                    }
                }
            }, {
                '$match': {
                    '_id': storage_id
                }
            }
        ])
        result = list(result)[0]['products']
        with open('Products.csv', 'w', encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["system_code", "name", "color", "guaranty", "storage_id", "quantity", "reserved"])
            for row in result:
                writer.writerow([row['system_code'], row['name'], row['color'], row['guaranty'], row['storage_id'],
                                 row['quantity'], row['reserved']])

        with open('Products.csv', 'rb') as f:
            data = f.read()
        os.remove('Products.csv')
        return data.decode("utf-8-sig")
