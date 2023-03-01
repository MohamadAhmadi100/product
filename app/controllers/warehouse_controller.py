from app.helpers import warehouses


def all_warehouses():
    return warehouses.warehouses()


def warehouse(storage_id):
    return warehouses.find_warehouse(storage_id)


def get_all_warehouses(all):
    result = warehouses.get_all_warehouses(all)
    if result:
        return {"success": True, "message": result, "status_code": 200}
    return {"success": False, "error": "something went wrong", "status_code": 404}


def create_warehouse(user_id, user_name, warehouse_id, warehouse_name, state, state_id, city, city_id, address):
    result = warehouses.create_warehouse_db(
        user_id, user_name, warehouse_id, warehouse_name, state, state_id, city, city_id, address
    )
    if result:
        return {"success": True, "message": "warehouse created successfully", "status_code": 201}
    return {"success": False, "error": "something went wrong", "status_code": 404}
