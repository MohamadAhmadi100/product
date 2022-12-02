from app.models.scm_quantity import *


def inv_initial_report(quantity_type):
    try:
        return initial_inv_report(quantity_type)
    except:
        return {'success': False, 'error': 'root exception error', 'status_code': 400}


def inv_products_report(storages, system_code, name, daily_system_code, daily_result):
    try:
        return inv_report(storages, system_code, name, daily_system_code, daily_result)
    except:
        return {'success': False, 'error': 'root exception error', 'status_code': 400}


def get_product_to_assign_qty(storage_id, system_code, customer_type):
    success, message = handle_get_product_to_assign_qty(storage_id, system_code, customer_type)

    if success:
        return {"message": message, "success": success, "status_code": 200}
    elif not success:
        return {"message": message, "success": success, "status_code": 417}
    else:
        return {"message": message, "success": success, "status_code": 500}


def assign_product_inventory(storage_id, system_code, customer_type, transfer, to_customer_type, quantity, min_qty,
                             max_qty, price, staff_id, staff_name):
    success, message = handle_assign_product_inventory(storage_id, system_code, customer_type, transfer,
                                                       to_customer_type, quantity, min_qty,
                                                       max_qty,
                                                       price, staff_id, staff_name)

    if success:
        return {"message": message, "success": success, "status_code": 200}
    elif not success:
        return {"message": message, "success": success, "status_code": 417}
    else:
        return {"message": message, "success": success, "status_code": 500}
