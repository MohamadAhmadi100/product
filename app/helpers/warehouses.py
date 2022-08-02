from app.helpers.mongo_connection import MongoConnection


def find_warehouse(storage_id):
    with MongoConnection() as client:
        result = client.warehouses.find_one({"warehouse_id": int(storage_id)})
        if result:
            return result
        else:
            return {}


def warehouses():
    with MongoConnection() as client:
        return list(client.warehouses.find())
