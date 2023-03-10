from app.models.order import exit_order_handler, rollback_products, imeis_rollback, handle_imei_checking, \
    get_cardex_report, get_imeis_report


def exit_order(order_number: int,
               storage_id: str,
               products: list,
               staff_id: int,
               staff_name: str,
               customer_type: str
               ):
    success, message = exit_order_handler(order_number,
                                          storage_id,
                                          products,
                                          staff_id,
                                          staff_name,
                                          customer_type)
    if success:
        return {"message": message, "success": success, "status_code": 200}
    elif not success:
        return {"message": message, "success": success, "status_code": 417}
    else:
        return {"message": message, "success": False, "status_code": 500}


def rollback_exit_order(rollback: list):
    imeis_rollback(rollback, rollback)
    rollback_products(rollback)
    return True


def check_imei(system_code: str, storage_id: str, imei: str):
    success, message = handle_imei_checking(system_code, storage_id, imei)
    if success:
        return {"message": message, "success": success, "status_code": 200}
    elif not success:
        return {"message": message, "success": success, "status_code": 417}
    else:
        return {"message": message, "success": False, "status_code": 500}


def get_cardex(page: int,
               per_page: int,
               sort_name: str,
               sort_type: str,
               system_code: str,
               storage_id: str,
               incremental_id: int,
               process_type: str
               ):
    success, message = get_cardex_report(page,
                                         per_page,
                                         sort_name,
                                         sort_type,
                                         system_code,
                                         storage_id,
                                         incremental_id,
                                         process_type
                                         )
    if success:
        return {"message": message, "success": success, "status_code": 200}
    elif not success:
        return {"message": message, "success": success, "status_code": 417}
    else:
        return {"message": message, "success": False, "status_code": 500}


def get_imeis(system_code: str, storage_id: str):
    success, message = get_imeis_report(system_code, storage_id)
    if success:
        return {"message": message, "success": success, "status_code": 200}
    elif not success:
        return {"message": message, "success": success, "status_code": 417}
    else:
        return {"message": message, "success": False, "status_code": 500}
