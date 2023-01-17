from app.helpers.warehouses import *


def all_warehouses():
    return warehouses()


def warehouse(storage_id):
    return find_warehouse(storage_id)


def create_warehouse(user_id, user_name, warehouse_id, warehouse_name, state, state_id, city, city_id, address):
    result = create_warehouse_db(
        user_id, user_name, warehouse_id, warehouse_name, state, state_id, city, city_id, address
    )
    if result:
        return {"success": True, "message": "warehouse created successfully", "status_code": 201}
    return {"success": False, "error": "something went wrong", "status_code": 404}
