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
            return export_transfer_form(products, transfer_object['src_warehouse'],
                                        transfer_object['dst_warehouse'],
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


def add_to_reserve_transfer(transfer_object, staff):
    check_data, add_cardex_to_quantity, data_response = list(), list(), list()
    for cursor_products in transfer_object.get("products"):
        reserve_result = create_transfer_reserve(cursor_products,
                                                 transfer_object['src_warehouse'],
                                                 transfer_object['dst_warehouse'],
                                                 transfer_object['referral_number'],
                                                 transfer_object['quantity_type'],
                                                 staff_name=staff,
                                                 )

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
                reserve_result = remove_reserve_rollback(reserved_products[0].get("system_code"),
                                                         transfer_object['src_warehouse'].get("storage_id"),
                                                         reserved_products[0].get("count"),
                                                         transfer_object['quantity_type'],
                                                         transfer_object['referral_number'])
                if reserve_result.get("success") is False:
                    return reserve_result
            else:
                data_response.append(reserved_products)
        return {'success': False, 'error': 'موجودی محصولات کافی نیست', "check_data": data_response,
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


def return_imei(order, imei, staff_name):
    order_model = OrderModel(dict(order))
    check_data, add_cardex_to_quantity, data_response = list(), list(), list()
    checked = False
    for cursor_products in order_model.return_order_data:
        if cursor_products.get("imei") == imei:
            reserve_reserve_result = return_order_items(cursor_products.get("system_code"),
                                                        cursor_products.get("storage_id"),
                                                        cursor_products.get("customer_type"),
                                                        cursor_products.get("order_number"),
                                                        cursor_products.get("imei"),
                                                        staff_name
                                                        )
            add_cardex_to_quantity.append(reserve_reserve_result.get('quantity_cardex_data'))
            checked = True

    if checked:
        try:
            add_to_cardex(order["customer"].get("id"), order["customer"].get('fullName'), order.get("orderNumber"),
                          add_cardex_to_quantity)
            return {'success': True, 'message': 'done', 'status_code': 200}
        except:
            return {'success': False, 'message': 'log error', 'status_code': 409}
    else:
        return {'success': False, 'message': 'عملیات ناموفقیت امیز بود', "check_data": data_response,
                'status_code': 200}


def return_order(order, staff_name):
    order_model = OrderModel(dict(order))
    check_data, add_cardex_to_quantity, data_response = list(), list(), list()
    for cursor_products in order_model.return_order_data:
        # add quantity per items
        reserve_reserve_result = return_order_items(cursor_products.get("system_code"),
                                                    cursor_products.get("storage_id"),
                                                    cursor_products.get("customer_type"),
                                                    cursor_products.get("order_number"),
                                                    cursor_products.get("imei"),
                                                    staff_name
                                                    )
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
        return {'success': False, 'message': 'عملیات ناموفقیت امیز بود', "check_data": data_response,
                'status_code': 200}


def edit_transfer_form(edit_object):
    check_data, add_cardex_to_quantity, data_response = list(), list(), list()
    # add reserve per items
    if edit_object['count'] < 0:
        reserve_result = remove_reserve_edit_transfer(edit_object.get("system_code"),
                                                      edit_object.get("storage_id"),
                                                      edit_object.get("count") * -1,
                                                      edit_object.get("customer_type"),
                                                      edit_object.get("referral_number"))
        add_cardex_to_quantity.append(reserve_result.get('quantity_cardex_data'))
        if reserve_result.get("success"):
            add_to_cardex(None, "staff", edit_object.get("referral_number"), add_cardex_to_quantity)
            return {'success': True, 'message': 'done', 'status_code': 200}
        else:
            return reserve_result
    elif edit_object['count'] > 0:
        reserve_result = add_to_reserve_edit_transfer(edit_object.get("system_code"),
                                                      edit_object.get("storage_id"),
                                                      edit_object.get("count"),
                                                      edit_object.get("customer_type"),
                                                      edit_object.get("referral_number"))
        add_cardex_to_quantity.append(reserve_result.get('quantity_cardex_data'))
        if reserve_result.get("success"):
            add_to_cardex(None, "staff", edit_object.get("referral_number"), add_cardex_to_quantity)
            return {'success': True, 'message': 'done', 'status_code': 200}
        else:
            return reserve_result


print(return_order({
    "orderNumber": 300000019,
    "status": "complete",
    "createdAt": "1401-05-18 22:58:29",
    "price": {
        "totalPrice": 700000,
        "grandPrice": 700000,
        "basePrice": 700000,
        "discount": 0
    },
    "total": {
        "totalQty": 1,
        "totalItem": 1
    },
    "payment": {
        "paymentId": None,
        "paymentMethod": [{
            "walletConsume": None
        }, {
            "bankMethod": "cashondelivery"
        }],
        "pos": True,
        "posDetails": {
            "transaction": None,
            "type": None,
            "recipt": None,
            "paymentDone": None,
            "processed": None
        }
    },
    "customer": {
        "fullName": "بهروز نوروزی زاده",
        "type": "B2B",
        "id": 3547,
        "mobile": "09353404849",
        "stateName": "خراسان رضوی",
        "stateId": "11",
        "cityName": "مشهد",
        "cityId": "1871",
        "address": "خ عبادی بین عبادی ٨٨ و ٩٠ ف دسترس",
        "email": "Lorka2012@yahoo.com",
        "shopName": None,
        "nId": "921532806",
        "kosarCode": "2804",
        "accFormalCode": "806060"
    },
    "logs": {
        "warehouseDetail": {
            "2": {
                "warehouseTime": "1401-05-19 10:08:31",
                "completeTime": "1401-05-19 11:40:35"
            },
            "warehouseTime": "1401-05-19 10:08:31",
            "completeTime": "1401-05-19 11:40:35"
        }
    },
    "totalStocks": 1,
    "splitedOrder": [{
        "status": "complete",
        "orderNumber": 300000019,
        "storageId": "1",
        "storageLabel": "مرکزی",
        "invStock": {
            "stockItems": 1,
            "stockQuantity": 1,
            "stockPrice": 700000
        },
        "totalStock": 1,
        "products": [{
            "status": "initial",
            "systemCode": "2000010020018003001021002",
            "name": "Xiaomi Redmi Note 11 Pro 5G (8GB 128GB 5G) Global | ASD | Sherkati [Graphite Gray]",
            "price": 8499000,
            "totalPrice": 16998000,
            "count": 2,
            "color": {
                "value": "Graphite Gray",
                "label": "Graphite Gray"
            },
            "brand": {
                "value": "Xiaomi",
                "label": "Xiaomi"
            },
            "model": "Redmi Note 11 Pro 5G",
            "category": {
                "value": "Device",
                "label": "Device"
            },
            "seller": {
                "value": "ASD",
                "label": "ASD"
            },
            "guarantee": {
                "value": "Sherkati",
                "label": "Sherkati"
            },
            "storageId": "1",
            "imeis": ["865346062537262", "865346062557880"]
        }, {
            "status": "initial",
            "systemCode": "2000010010014002001001002",
            "name": "Samsung A52 (8GB 128GB 4G) India | ASD | Sherkati [Black]",
            "price": 8299000,
            "totalPrice": 8299000,
            "count": 1,
            "color": {
                "value": "Black",
                "label": "Black"
            },
            "brand": {
                "value": "Samsung",
                "label": "Samsung"
            },
            "model": "A52",
            "category": {
                "value": "Device",
                "label": "Device"
            },
            "seller": {
                "value": "ASD",
                "label": "ASD"
            },
            "guarantee": {
                "value": "Sherkati",
                "label": "Sherkati"
            },
            "storageId": "1",
            "imeis": ["354254222532199"]
        }, {
            "status": "initial",
            "systemCode": "2000010010005006001001001",
            "name": "Samsung A03s (4GB 64GB 4G) RX | ASD | Aawaat [Black]",
            "price": 3699000,
            "totalPrice": 3699000,
            "count": 1,
            "color": {
                "value": "Black",
                "label": "Black"
            },
            "brand": {
                "value": "Samsung",
                "label": "Samsung"
            },
            "model": "A03s",
            "category": {
                "value": "Device",
                "label": "Device"
            },
            "seller": {
                "value": "ASD",
                "label": "ASD"
            },
            "guarantee": {
                "value": "Aawaat",
                "label": "Aawaat"
            },
            "storageId": "1",
            "imeis": ["350060030290589"]
        }],
        "shipment": {
            "priceLabel": "رایگان",
            "shipmentPrice": 0,
            "customerPrice": 0,
            "customerDiscount": 0,
            "shippingLabel": "تحویل درب انبار آسود",
            "shippingMethod": "aasood",
            "shippingAddress": "خ عبادی بین عبادی ٨٨ و ٩٠ ف دسترس",
            "shippingCity": "مشهد",
            "shippingCityId": "1871",
            "shippingState": "خراسان رضوی",
            "shippingStateId": "11",
            "shippingMobile": "",
            "receiverFirstName": "",
            "receiverLastName": "",
            "receiverNationalId": "",
            "receiverPhoneNumber": "",
            "insurance": {
                "insuranceType": "aasood",
                "typeLabel": "فاقد بیمه",
                "amount": 0,
                "coverage": "بیشترین ارزش بسته:",
                "selectedType": "fullCart"
            }
        }
    }],
    "dealership": False,
    "createdAtMiladi": "2022-08-09 22:58:29"
})
)
