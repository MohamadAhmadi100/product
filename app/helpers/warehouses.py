import jdatetime

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


def create_warehouse_db(user_id, user_name, warehouse_id, warehouse_name, state, state_id, city, city_id, address):
    with MongoConnection() as mongo:
        result = mongo.warehouses.insert_one({
            "user_id": user_id,
            "user_name": user_name,
            "warehouse_id": warehouse_id,
            "warehouse_name": warehouse_name,
            "kosar_id": warehouse_id,
            "warehouse_status": 1,
            "warehouse_type": [
                "virtual",
                "physical"
            ],
            "establishment_status": "static",
            "assigned_customers": None,
            "assigned_cities": None,
            "state": state,
            "state_id": state_id,
            "city": city,
            "city_id": city_id,
            "address": address,
            "warehouse_tel": "",
            "warehouse_admin": "",
            "warehouse_admin_tel": "",
            "logistic_admin": "",
            "logistic_admin_tel": "",
            "staff": [],
            "insert_date": jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "isActive": False
        })
    if result.inserted_id:
        return True
    return False
