from app.models.order import exit_order_handler, rollback_products, imeis_rollback, handle_imei_checking


def exit_order(order_number,
               storage_id,
               products,
               staff_id,
               staff_name):
    success, message = exit_order_handler(order_number,
                                  storage_id,
                                  products,
                                  staff_id,
                                  staff_name)
    if success:
        return {"message": message, "success": success, "status_code": 200}
    elif not success:
        return {"message": message, "success": success, "status_code": 417}
    else:
        return {"message": message, "success": False, "status_code": 500}


def rollback_exit_order(rollback):

    imeis_rollback(rollback, rollback)
    rollback_products(rollback)
    return True


def check_imei(system_code,storage_id,imei):

    success, message = handle_imei_checking(system_code,storage_id,imei)
    if success:
        return {"message": message, "success": success, "status_code": 200}
    elif not success:
        return {"message": message, "success": success, "status_code": 417}
    else:
        return {"message": message, "success": False, "status_code": 500}



