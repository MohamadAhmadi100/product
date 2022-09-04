from app.helpers.warehouses import warehouses
from app.reserve_quantity.cardex import add_to_cardex
from app.reserve_quantity.route_actions import *

"""
order
"""


def add_to_reserve(order):
    order_model = OrderModel(dict(order))
    check_data, add_cardex_to_quantity, data_response = list(), list(), list()
    for cursor_products in order_model.order_data:
        # add reserve per items
        reserve_reserve_result = add_to_reserve_order(cursor_products.get("system_code"),
                                                      cursor_products.get("storage_id"),
                                                      cursor_products.get("count"),
                                                      cursor_products.get("customer_type"),
                                                      cursor_products.get("sku"),
                                                      cursor_products.get("order_number"))
        data_for_check = (cursor_products, reserve_reserve_result.get("success"))
        check_data.append(data_for_check)
        add_cardex_to_quantity.append(reserve_reserve_result.get('quantity_cardex_data'))
    # check all items reserved
    checked = all(elem[1] for elem in check_data)
    if checked:
        try:
            add_to_cardex(order["customer"].get("id"), order["customer"].get('fullName'), order.get("orderNumber"),
                          add_cardex_to_quantity)
            return {'success': True, 'message': 'done', 'status_code': 200}
        except:
            return {'success': False, 'message': 'log error', 'status_code': 409}
    else:
        # roll back
        for reserved_products in check_data:
            if reserved_products[1] is True:
                reserve_result = remove_reserve_rollback(reserved_products[0].get("system_code"),
                                                         reserved_products[0].get("storage_id"),
                                                         reserved_products[0].get("count"),
                                                         reserved_products[0].get("customer_type"),
                                                         reserved_products[0].get("order_number"))
                if reserve_result.get("success") is False:
                    return reserve_result
                data_response.append(reserved_products)
        return {'success': False, 'message': 'operation unsuccessful', "check_data": data_response, 'status_code': 200}


def remove_from_reserve(order):
    order_model = OrderModel(dict(order))
    check_data, add_cardex_to_quantity, data_response = list(), list(), list()
    for cursor_products in order_model.order_data:
        # add reserve per items
        reserve_result = remove_reserve_cancel(cursor_products.get("system_code"),
                                               cursor_products.get("storage_id"),
                                               cursor_products.get("count"),
                                               cursor_products.get("customer_type"),
                                               cursor_products.get("sku"),
                                               cursor_products.get("order_number"))
        data_for_check = (cursor_products, reserve_result.get("success"))
        check_data.append(data_for_check)
        add_cardex_to_quantity.append(reserve_result.get('quantity_cardex_data'))
    checked = all(elem[1] for elem in check_data)
    # check all items reserved
    if checked:
        try:
            add_to_cardex(order["customer"].get("id"), order["customer"].get('fullName'), order.get("orderNumber"),
                          add_cardex_to_quantity)
            return {'success': True, 'message': 'done', 'status_code': 200}
        except:
            return {'success': False, 'message': 'log error', 'status_code': 409}
    else:
        # roll back
        for reserved_products in check_data:
            if reserved_products[1] is True:
                reserve_result = add_reserve_rollback(reserved_products[0].get("system_code"),
                                                      reserved_products[0].get("storage_id"),
                                                      reserved_products[0].get("count"),
                                                      reserved_products[0].get("customer_type"),
                                                      reserved_products[0].get("order_number"))
                if reserve_result.get("success") is False:
                    return reserve_result
            else:
                data_response.append(reserved_products)
        return {'success': False, 'message': 'operation unsuccessful', "error": data_response,
                'status_code': 200}


def remove_reserve_edit(edited_object, order_number, customer_id, customer_type, customer_name):
    add_cardex_to_quantity, check_data, data_response = list(), list(), list()

    for cursor_products in edited_object:
        # add reserve per items
        reserve_result = remove_reserve_edit_order(cursor_products.get("systemCode"),
                                                   cursor_products.get("storageId"),
                                                   (int(cursor_products.get("oldCount")) - int(
                                                       cursor_products.get("newCount"))),
                                                   customer_type, cursor_products.get("sku"),
                                                   cursor_products.get("order_number"))
        data_for_check = (cursor_products, reserve_result.get("success"))
        check_data.append(data_for_check)
        add_cardex_to_quantity.append(reserve_result.get("quantity"))
    # check all items reserved
    checked = all(elem[1] for elem in check_data)
    if checked:
        try:
            add_to_cardex(customer_id, customer_name, order_number, add_cardex_to_quantity)
            return {'success': True, 'message': 'done', 'status_code': 200}
        except:
            return {'success': False, 'message': 'log error', 'status_code': 409}
    else:
        # roll back
        for reserved_products in check_data:
            if reserved_products[1] is True:
                reserve_result = add_reserve_rollback(reserved_products[0].get("systemCode"),
                                                      reserved_products[0].get("storageId"),
                                                      reserved_products[0].get("count"),
                                                      reserved_products[0].get("customer_type"),
                                                      order_number)
                if reserve_result.get("success") is False:
                    return reserve_result
            else:
                data_response.append(reserved_products)
        return {'success': False, 'message': 'operation unsuccessful', "error": data_response,
                'status_code': 200}


"""
dealership
"""


def add_to_reserve_dealership(referral_number, customer_id, customer_type, data):
    check_data, data_response, add_cardex_to_quantity = list(), list(), list()
    for cursor_products in data.get("products"):
        # add reserve per items
        reserve_result = add_to_reserve_dealership(cursor_products.get("system_code"),
                                                   cursor_products.get("storage_id"),
                                                   cursor_products.get("count"),
                                                   customer_type[0], cursor_products.get("name"),
                                                   referral_number)

        data_for_check = (cursor_products, reserve_result.get("success"))
        check_data.append(data_for_check)
        add_cardex_to_quantity.append(reserve_result.get("quantity"))
    # check all items reserved
    checked = all(elem[1] for elem in check_data)
    if checked:
        try:
            add_to_cardex(customer_id, None, referral_number, add_cardex_to_quantity)
            return {'success': True, 'message': 'done', 'status_code': 200}
        except:
            return {'success': False, 'message': 'log error', 'status_code': 409}
    else:
        # roll back
        for reserved_products in check_data:
            if reserved_products[1] is True:
                reserve_result = remove_reserve_rollback(reserved_products[0].get("systemCode"),
                                                         reserved_products[0].get("storageId"),
                                                         reserved_products[0].get("count"),
                                                         reserved_products[0].get("customer_type"),
                                                         referral_number)
                if reserve_result.get("success") is False:
                    return reserve_result
            else:
                data_response.append(reserved_products)
        return {'success': False, 'message': 'operation unsuccessful', "check_data": data_response, 'status_code': 200}


"""
warehouse
"""


def warehouse_buying(product, dst_warehouse, referral_number, supplier_name, form_date, customer_type):
    check = check_buying_imeis(product)
    if check.get("success"):
        master_product = add_warehouse_product(product, referral_number, supplier_name, form_date, dst_warehouse)
        if master_product.get("success"):
            product_reserve_result = add_buying_form(product, dst_warehouse, customer_type,
                                                     referral_number,
                                                     supplier_name, form_date)
            if product_reserve_result.get("success"):
                product_reserve_result['message'] = "عملیات با موفقیت انجام شد"
                return product_reserve_result
            else:
                return product_reserve_result
        else:
            return master_product
    else:
        return check


def transfer_products(transfer_object, system_code, staff_name):
    global products
    try:
        for cursor_products in transfer_object['products']:
            if cursor_products['system_code'] == system_code:
                products = cursor_products

        if transfer_object['status_type'] == "submit":
            return export_transfer_form(products, transfer_object['dst_warehouse'],
                                        transfer_object['src_warehouse'],
                                        transfer_object['referral_number'],
                                        transfer_object['quantity_type'], 'staff')
        elif transfer_object['status_type'] == "transfer":
            return import_transfer_form(products, transfer_object['dst_warehouse'],
                                        transfer_object['src_warehouse'],
                                        transfer_object['referral_number'],
                                        transfer_object['quantity_type'], 'staff')
        return {'success': False, 'error': 'status not fount', 'status_code': 400}
    except:
        return {'success': False, 'error': 'root exception error', 'status_code': 400}


def add_to_reserve_transfer(transfer_object):
    check_data, add_cardex_to_quantity, data_response = list(), list(), list()
    for cursor_products in transfer_object.get("products"):
        reserve_result = create_transfer_reserve(cursor_products.get("system_code"),
                                                 transfer_object['src_warehouse'].get("storage_id"),
                                                 cursor_products.get("count"),
                                                 transfer_object['quantity_type'],
                                                 cursor_products.get("name"),
                                                 transfer_object['referral_number'])

        data_for_check = (cursor_products, reserve_result.get("success"))
        check_data.append(data_for_check)
        add_cardex_to_quantity.append(reserve_result.get('quantity_cardex_data'))
    checked = all(elem[1] for elem in check_data)
    if checked:
        try:
            add_to_cardex("staff", None, transfer_object['referral_number'],
                          add_cardex_to_quantity)
            return {'success': True, 'message': 'فرم انتقالی با موفقیت ثبت شد', 'status_code': 200}
        except:
            return {'success': False, 'error': 'log error', 'status_code': 409}
    else:
        for reserved_products in check_data:
            if reserved_products[1] is True:
                reserve_result = remove_reserve_rollback(reserved_products[0].get("systemCode"),
                                                         reserved_products[0].get("storageId"),
                                                         reserved_products[0].get("count"),
                                                         reserved_products[0].get("customer_type"),
                                                         transfer_object['referral_number'])
                if reserve_result.get("success") is False:
                    return reserve_result
            else:
                data_response.append(reserved_products)
        return {'success': False, 'message': 'operation unsuccessful', "check_data": data_response,
                'status_code': 200}


def check_transfer_imeis(imei, transfer_object):
    try:
        return check_transfer_imei(imei, transfer_object)
    except:
        return {'success': False, 'error': 'root exception error', 'status_code': 400}


def all_warehouses():
    return warehouses()


def warehouse(storage_id):
    return find_warehouse(storage_id)


def return_imei(system_code, storage_id, customer_type, order_number, imeis):
    add_cardex_to_quantity = []
    reserve_result = return_order_items(system_code, storage_id, customer_type, order_number, imeis)
    if reserve_result.get("success"):
        add_cardex_to_quantity.append(reserve_result.get('quantity_cardex_data'))
        add_to_cardex("staff", None, order_number, add_cardex_to_quantity)
        reserve_result.pop("quantity_cardex_data")
        return reserve_result
    else:
        return reserve_result
