from app.reserve_quantity.reserve import Reserve

"""
order
"""


def remove_from_reserve(order):
    order_model = Reserve(dict(order))
    add_cardex_to_msm, add_cardex_to_quantity = list(), list()
    for item in order_model.order_data:
        result = order_model.remove_reserve_cancel(item.get("system_code"), item.get("storage_id"), item.get("count"),
                                                   item.get("customer_type"), item.get("sku"), item.get("order_number"))
        add_cardex_to_quantity.append(result.get("quantity"))
        if result.get("success") is False:
            return result
    try:
        Reserve.cardex(order["customer"].get("id"), order["customer"].get("fullName"), order.get("orderNumber"),
                       add_cardex_to_quantity)
        return {'success': True, 'message': 'done', 'status_code': 200}
    except:
        return {'success': False, 'message': 'log error', 'status_code': 409}


def add_to_reserve(order):
    order_model = Reserve(dict(order))
    check_data, add_cardex_to_quantity = list(), list()
    for item in order_model.order_data:
        result = order_model.add_to_reserve_order(item.get("system_code"), item.get("storage_id"), item.get("count"),
                                                  item.get("customer_type"), item.get("sku"), item.get("order_number"))

        data_for_check = (item, result.get("success"))
        check_data.append(data_for_check)
        add_cardex_to_quantity.append(result.get("quantity"))
    checked = all(elem[1] for elem in check_data)
    if checked:
        try:
            Reserve.cardex(order["customer"].get("id"), order["customer"].get('fullName'), order.get("orderNumber"),
                           add_cardex_to_quantity)
            return {'success': True, 'message': 'done', 'status_code': 200}
        except:
            return {'success': False, 'message': 'log error', 'status_code': 409}
    else:
        for data in check_data:
            if data[1] is True:
                result = order_model.remove_reserve_cancel(data[0].get("system_code"), data[0].get("storage_id"),
                                                           data[0].get("count"), data[0].get("customer_type"),
                                                           data[0].get("sku"), data[0].get("order_number"))
                if result.get("success") is False:
                    return result
        return {'success': False, 'message': 'operation unsuccessful', "check_data": check_data, 'status_code': 200}


def remove_reserve_edit(edited_object, order_number, customer_id, customer_type, customer_name):
    add_cardex_to_quantity = list()

    for item in edited_object:
        result = Reserve.remove_reserve_edit_order(item.get("systemCode"), item.get("storageId"),
                                                   (int(item.get("oldCount")) - int(item.get("newCount"))),
                                                   customer_type, item.get("sku"), item.get("order_number"))
        if result.get("success") is False:
            return result
        add_cardex_to_quantity.append(result.get("quantity"))

    try:
        Reserve.cardex(customer_id, customer_name, order_number, add_cardex_to_quantity)
        return {'success': True, 'message': 'done', 'status_code': 200}
    except:
        return {'success': False, 'message': 'log error', 'status_code': 409}


"""
dealership
"""


def add_to_reserve_dealership(referral_number, customer_id, customer_type, data):
    check_data, add_cardex_to_quantity = list(), list()
    for item in data.get("products"):
        result = Reserve.add_to_reserve_dealership(item.get("systemCode"), item.get("storageId"), item.get("count"),
                                                   customer_type[0], item.get("name"), referral_number)

        data_for_check = (item, result.get("success"))
        check_data.append(data_for_check)
        add_cardex_to_quantity.append(result.get("quantity"))
    checked = all(elem[1] for elem in check_data)
    if checked:
        try:

            Reserve.cardex(customer_id, None, referral_number,
                           add_cardex_to_quantity)
            return {'success': True, 'message': 'done', 'status_code': 200}
        except:
            return {'success': False, 'message': 'log error', 'status_code': 409}
    else:
        for element in check_data:
            if element[1] is True:
                result = Reserve.remove_reserve_cancel(element[0].get("systemCode"), element[0].get("storageId"),
                                                       element[0].get("count"), element[0].get("customer_type"),
                                                       element[0].get("name"), referral_number)
                if result.get("success") is False:
                    return result
        return {'success': False, 'message': 'operation unsuccessful', "check_data": check_data, 'status_code': 200}
