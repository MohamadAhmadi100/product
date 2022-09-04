from app.models.order import exit_order_handler


def exit_order(order_number,
               storage_id,
               products,
               staff_id,
               staff_name):
    response = exit_order_handler(order_number,
                                  storage_id,
                                  products,
                                  staff_id,
                                  staff_name)
    success, message = response
    if success:
        return {"message": message, "success": success, "status_code": 200}
    elif not success:
        return {"message": message, "success": success, "status_code": 417}
    else:
        return {"message": message, "success": False, "status_code": 500}
