from app.helpers.mongo_connection import MongoConnection


def find_warehouse(storage_id):
    with MongoConnection() as client:
        result = client.warehouses.find_one({"warehouse_id": int(storage_id)}, {"_id": False})
        if result:
            return {"success": True, "warehouses": result}
        else:
            return {"success": False, "error": "انبار اشتباه است"}


def warehouses():
    with MongoConnection() as client:
        warehouses = list(client.warehouses.find({}, {"_id": False}))
        return {"success": True, "warehouses": warehouses}
