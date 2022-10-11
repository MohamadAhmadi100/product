from app.helpers.mongo_connection import MongoConnection
import jdatetime


def balanced_avg():
    """
    get balanced avg
    """
    with MongoConnection() as client:
        products_col = client.archive.find({"articles.exist": True})
        bavg_result = []
        bavg_system_code = []
        for root in products_col:
            try:
                counter = 0
                for articles in root['articles']:
                    if articles['exist'] == True:
                        counter += 1
                if counter > 0:
                    mozon = counter * root['unit_price']
                    if root['system_code'] not in bavg_system_code:
                        bavg_system_code.append(root['system_code'])
                        bavg_result.append({
                            "systemCode": root['system_code'],
                            "mozon": mozon,
                            "counter": counter
                        })
                    else:
                        index = bavg_system_code.index(root['partNumber'])
                        bavg_result[index]["mozon"] += mozon
                        bavg_result[index]["counter"] += counter
            except:
                pass
        for items in bavg_result:
            items['result'] = int(items['mozon'] / items['counter'])
        return bavg_system_code, bavg_result


def categorized_data(result):
    """
    categorized product result in inv_report function
    """
    categorize = []
    for items in result:
        name = items['sku']
        cats = [i["category"] for i in categorize]
        if items["cat"] in cats:
            index_cat = cats.index(items["cat"])
            sub_cat = [z['subCategory'] for z in categorize[index_cat]["subCategories"]]
            if items['subCat'] in sub_cat:
                index_sub = sub_cat.index(items['subCat'])
                brands = [j["brand"] for j in categorize[index_cat]["subCategories"][index_sub]['brands']]
                if items["brand"] in brands:
                    index_brand = brands.index(items["brand"])
                    models = [j["model"] for j in
                              categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"]]
                    if items["model"] in models:
                        index_model = models.index(items["model"])
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"][
                            index_model]["items"].append({
                            "systemCode": items['systemCode'],
                            "sku": name,
                            "model": items['model'],
                            "seller": items['seller'],
                            "color": items['color'],
                            "guaranty": items['guaranty'],
                            "stockId": items['stockId'],
                            "quantity": items['quantity'],
                            "reserve": items['reserve'],
                            "salable": items['salable'],
                            "dailySales": items.get('dailySales'),
                            "balancedAvg": items['balancedAvg'],
                            "price": items['price'],

                        })
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"][
                            index_model]['total_count'] += items['quantity']
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"][
                            index_model]['total_price'] += items['price'] * items['quantity']
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['total_count'] += \
                            items['quantity']
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['total_price'] += \
                            items['price'] * items['quantity']
                        categorize[index_cat]['total_count'] += items['quantity']
                        categorize[index_cat]['total_price'] += items['price'] * items[
                            'quantity']

                        categorize[index_cat]['subCategories'][index_sub]['total_count'] += items['quantity']
                        categorize[index_cat]['subCategories'][index_sub]['total_price'] += items['price'] * items[
                            'quantity']
                        categorize[index_cat]['dailySales'] += items['dailySales']
                        categorize[index_cat]['subCategories'][index_sub]['dailySales'] += items['dailySales']
                        categorize[index_cat]['subCategories'][index_sub]['brands'][index_brand]['dailySales'] += items[
                            'dailySales']
                        categorize[index_cat]['subCategories'][index_sub]['brands'][index_brand]['models'][index_model][
                            'dailySales'] += items['dailySales']
                    else:
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"].append(
                            {
                                "model": items["model"],
                                "total_count": items['quantity'],
                                "total_price": items['price'],
                                "dailySales": items['dailySales'],
                                "items": [
                                    {
                                        "systemCode": items['systemCode'],
                                        "sku": name,
                                        "model": items['model'],
                                        "seller": items['seller'],
                                        "color": items['color'],
                                        "guaranty": items['guaranty'],
                                        "stockId": items['stockId'],
                                        "quantity": items['quantity'],
                                        "reserve": items['reserve'],
                                        "salable": items['salable'],
                                        "dailySales": items['dailySales'],
                                        "balancedAvg": items['balancedAvg'],
                                        "price": items['price'],

                                    }
                                ]
                            })
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['total_count'] += \
                            items['quantity']
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['total_price'] += \
                            items['price'] * items['quantity']
                        categorize[index_cat]['total_count'] += items['quantity']
                        categorize[index_cat]['total_price'] += items['price'] * items[
                            'quantity']

                        categorize[index_cat]['subCategories'][index_sub]['total_count'] += items['quantity']
                        categorize[index_cat]['subCategories'][index_sub]['total_price'] += items['price'] * items[
                            'quantity']

                        categorize[index_cat]['dailySales'] += items['dailySales']
                        categorize[index_cat]['subCategories'][index_sub]['dailySales'] += items['dailySales']
                        categorize[index_cat]['subCategories'][index_sub]['brands'][index_brand]['dailySales'] += items[
                            'dailySales']

                else:
                    categorize[index_cat]["subCategories"][index_sub]['brands'].append({
                        "brand": items["brand"],
                        "total_count": items['quantity'],
                        "total_price": items['price'],
                        "dailySales": items['dailySales'],
                        "models": [
                            {
                                "model": items["model"],
                                "total_count": items['quantity'],
                                "total_price": items['price'],
                                "dailySales": items['dailySales'],
                                "items": [
                                    {
                                        "systemCode": items['systemCode'],
                                        "sku": name,
                                        "model": items['model'],
                                        "seller": items['seller'],
                                        "color": items['color'],
                                        "guaranty": items['guaranty'],
                                        "stockId": items['stockId'],
                                        "quantity": items['quantity'],
                                        "reserve": items['reserve'],
                                        "salable": items['salable'],
                                        "dailySales": items['dailySales'],
                                        "balancedAvg": items['balancedAvg'],
                                        "price": items['price'],

                                    }
                                ]
                            }
                        ]
                    })
                    categorize[index_cat]['total_count'] += items['quantity']
                    categorize[index_cat]['total_price'] += items['price'] * items[
                        'quantity']

                    categorize[index_cat]['subCategories'][index_sub]['total_count'] += items['quantity']
                    categorize[index_cat]['subCategories'][index_sub]['total_price'] += items['price'] * items[
                        'quantity']
                    categorize[index_cat]['dailySales'] += items['dailySales']
                    categorize[index_cat]['subCategories'][index_sub]['dailySales'] += items['dailySales']
            else:
                categorize[index_cat]["subCategories"].append({
                    "subCategory": items['subCat'],
                    "total_count": items['quantity'],
                    "total_price": items['price'],
                    "dailySales": items['dailySales'],
                    "brands": [
                        {
                            "brand": items["brand"],
                            "total_count": items['quantity'],
                            "total_price": items['price'],
                            "dailySales": items['dailySales'],
                            "models": [
                                {
                                    "model": items["model"],
                                    "total_count": items['quantity'],
                                    "total_price": items['price'],
                                    "dailySales": items['dailySales'],
                                    "items": [
                                        {
                                            "systemCode": items['systemCode'],
                                            "sku": name,
                                            "model": items['model'],
                                            "seller": items['seller'],
                                            "color": items['color'],
                                            "guaranty": items['guaranty'],
                                            "stockId": items['stockId'],
                                            "quantity": items['quantity'],
                                            "reserve": items['reserve'],
                                            "salable": items['salable'],
                                            "dailySales": items['dailySales'],
                                            "balancedAvg": items['balancedAvg'],
                                            "price": items['price'],

                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                })
                categorize[index_cat]['total_count'] += items['quantity']
                categorize[index_cat]['total_price'] += items['price'] * items[
                    'quantity']
                categorize[index_cat]['dailySales'] += items['dailySales']

        else:
            categorize.append({
                "category": items["cat"],
                "total_count": items['quantity'],
                "total_price": items['price'],
                "dailySales": items['dailySales'],
                "subCategories": [{
                    "subCategory": items['subCat'],
                    "total_count": items['quantity'],
                    "total_price": items['price'],
                    "dailySales": items['dailySales'],
                    "brands": [
                        {
                            "brand": items["brand"],
                            "total_count": items['quantity'],
                            "total_price": items['price'],
                            "dailySales": items['dailySales'],
                            "models": [
                                {
                                    "model": items["model"],
                                    "total_count": items['quantity'],
                                    "total_price": items['price'],
                                    "dailySales": items['dailySales'],
                                    "items": [
                                        {
                                            "systemCode": items['systemCode'],
                                            "sku": name,
                                            "model": items['model'],
                                            "seller": items['seller'],
                                            "color": items['color'],
                                            "guaranty": items['guaranty'],
                                            "stockId": items['stockId'],
                                            "quantity": items['quantity'],
                                            "reserve": items['reserve'],
                                            "salable": items['salable'],
                                            "dailySales": items['dailySales'],
                                            "balancedAvg": items['balancedAvg'],
                                            "price": items['price'],

                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }]})

    return categorize


def inv_report(storages, system_code, name, daily_system_code, daily_result):
    """
    get data from products where quantity above 0
    """
    try:
        with MongoConnection() as client:
            query = {}
            if system_code is not None:
                query['system_code'] = system_code
            if name is not None:
                query['$or'] = [{"name": {"$regex": name}}]

            bavg_system_code, bavg_result = balanced_avg()
            product = client.product.find(query, {"_id": False})
            result = []
            for items in product:
                data = {}
                total_count = 0
                total_price = 0
                if items['step'] == 4:
                    for key, value in items['warehouse_details'].items():
                        if value.get("storages") is None:
                            pass
                        else:
                            data['customer_type'] = key
                            for storage_key, storage_value, in value['storages'].items():
                                if storage_value['storage_id'] in storages:
                                    if storage_value.get('quantity') is not None and storage_value.get('quantity') > 0:
                                        total_count += storage_value['quantity']
                                        total_price += storage_value['regular'] * storage_value['quantity']
                                        # daily sales
                                        if {"systemCode": items['system_code'],
                                            "stockId": storage_value['storage_id']} in daily_system_code:
                                            index = daily_system_code.index(
                                                {"systemCode": items['system_code'],
                                                 "stockId": storage_value['storage_id']})
                                            daily_sale = daily_result[index]['count']
                                        else:
                                            daily_sale = 0
                                        # balanced avg
                                        if items['system_code'] in bavg_system_code:
                                            index_bavg = bavg_system_code.index(items['system_code'])
                                            bavg_sale = bavg_result[index_bavg]['result']
                                        else:
                                            bavg_sale = 0

                                        result.append({
                                            "systemCode": items['system_code'],
                                            "sku": items['name'],
                                            "model": items['model'],
                                            "seller": items['seller'],
                                            "color": items['color'],
                                            "brand": items['brand'],
                                            "cat": items['main_category'],
                                            "subCat": items['sub_category'],
                                            "guaranty": items['guaranty'],
                                            "stockId": storage_value['storage_id'],
                                            "quantity": storage_value['quantity'],
                                            "reserve": storage_value['reserved'],
                                            "salable": storage_value['quantity'] - storage_value['reserved'],
                                            "dailySales": daily_sale,
                                            "balancedAvg": bavg_sale,
                                            "price": storage_value['regular'],
                                            "customer_type": key
                                        })
                                    else:
                                        pass
                else:
                    pass
            # build object for response
            result_categorize = categorized_data(result)

            return {"success": True, "result": result_categorize, "status_code": 200}
    except:
        pass


def initial_inv_report(quantity_type):
    """
    initial data for scm dashboard
    """
    with MongoConnection() as client:
        total = client.product.aggregate([
            {
                '$project': {
                    'storages': {
                        '$objectToArray': f'$warehouse_details.{quantity_type}.storages'
                    }
                }
            }, {
                '$addFields': {
                    'storage': '$storages.v'
                }
            }, {
                '$project': {
                    '_id': 0,
                    'storages': 0
                }
            }, {
                '$unwind': {
                    'path': '$storage'
                }
            }, {
                '$match': {
                    'storage.quantity': {
                        '$gte': 1
                    }
                }
            }, {
                '$group': {
                    '_id': None,
                    'totalQuantity': {
                        '$sum': '$storage.quantity'
                    },
                    'totalPrice': {
                        '$sum': {
                            '$multiply': [
                                '$storage.quantity', '$storage.regular'
                            ]
                        }
                    }
                }
            }, {
                '$project': {
                    '_id': 0
                }
            }
        ])
        storages = client.product.aggregate([
            {
                '$project': {
                    'storages': {
                        '$objectToArray': f'$warehouse_details.{quantity_type}.storages'
                    }
                }
            }, {
                '$addFields': {
                    'storage': '$storages.v'
                }
            }, {
                '$project': {
                    '_id': 0,
                    'storages': 0
                }
            }, {
                '$unwind': {
                    'path': '$storage'
                }
            }, {
                '$match': {
                    'storage.quantity': {
                        '$gte': 1
                    }
                }
            }, {
                '$group': {
                    '_id': '$storage.storage_id',
                    'totalQuantity': {
                        '$sum': '$storage.quantity'
                    },
                    'totalPrice': {
                        '$sum': {
                            '$multiply': [
                                '$storage.quantity', '$storage.regular'
                            ]
                        }
                    }
                }
            }, {
                '$project': {
                    '_id': 0,
                    'storageId': '$_id',
                    'totalQuantity': 1,
                    'totalPrice': 1
                }
            }
        ])

        if total.alive and storages.alive:
            total_result = list(total)[0]
            return {"success": True, "stocks": list(storages), "totalPrice": total_result['totalPrice'],
                    "totalQuantity": total_result['totalQuantity']}
        else:
            return {"success": True, "stocks": [], "totalPrice": 0,
                    "totalQuantity": 0}


def handle_get_product_to_assign_qty(storage_id, system_code, customer_type):
    try:

        product_object = get_product_query(system_code)
        if not product_object:
            return False, "محصولی یافت نشد"
        customer_type_object = get_customer_type_object(product_object, storage_id, customer_type)
        if not customer_type_object:
            return False, "محصولی با نوع مشتری مورد نظر پیدا نشد"
    except Exception:
        return False, "خطای سیستمی رخ داده است"


def handle_assign_product_inventory(storage_id, system_code, customer_type, transfer, to_customer_type, quantity,
                                    min_qty,
                                    max_qty,
                                    price, staff_id, staff_name):
    try:
        product_object = get_product_query(system_code)
        if not product_object:
            return False, "محصولی یافت نشد"
        customer_type_object = get_customer_type_object(product_object, storage_id, customer_type)
        if not customer_type_object:
            return False, "محصولی با نوع مشتری مورد نظر پیدا نشد"

        if transfer:
            to_customer_type_object = get_customer_type_object(product_object, storage_id, to_customer_type)
            if not customer_type_object:
                return False, "محصولی با نوع مشتری مورد نظر پیدا نشد"
            from_cardex = handle_cardex(customer_type_object, storage_id, system_code, quantity, staff_id, staff_name,
                                        f"transferto_{to_customer_type}", customer_type)

            to_cardex = handle_cardex(to_customer_type_object, storage_id, system_code, quantity, staff_id, staff_name,
                                      f"transferfrom_{customer_type}", to_customer_type)

            success, message = transfer_product_inventory(customer_type_object, to_customer_type_object, quantity,
                                                          min_qty,
                                                          max_qty,
                                                          price)
            if not success:
                return success, message
            if not product_query(system_code, product_object):
                return False, "خطا در بروز رسانی"
            from_cardex["new_quantity"] = customer_type_object["quantity"]
            from_cardex["new_reserve"] = customer_type_object["reserved"]
            from_cardex["new_inventory"] = customer_type_object["inventory"]
            cardex_query(from_cardex)

            to_cardex["new_quantity"] = customer_type_object["quantity"]
            to_cardex["new_reserve"] = customer_type_object["reserved"]
            to_cardex["new_inventory"] = customer_type_object["inventory"]
            cardex_query(to_cardex)

            return True, "عملیات با موفقیت انجام شد"

        cardex = handle_cardex(customer_type_object, storage_id, system_code, quantity, staff_id, staff_name,
                               "editQuantity", customer_type)
        success, message = edit_product_inventory(customer_type_object, quantity, min_qty,
                                                  max_qty)
        if not success:
            return success, message
        if not product_query(system_code, product_object):
            return False, "خطا در بروز رسانی"
        cardex["new_quantity"] = customer_type_object["quantity"]
        cardex["new_reserve"] = customer_type_object["reserved"]
        cardex["new_inventory"] = customer_type_object["inventory"]
        cardex_query(cardex)
        return True, "عملیات با موفقیت انجام شد"
    except Exception:
        return False, "خطای سیستمی رخ داده است"


def transfer_product_inventory(customer_type_object, to_customer_type_object, quantity, min_qty,
                               max_qty,
                               price):
    try:
        if customer_type_object["inventory"] - customer_type_object["quantity"] < quantity:
            return False, "مجاز به انتقال نمی باشید"

        if "inventory" in to_customer_type_object and "quantity" in to_customer_type_object:
            to_customer_type_object["inventory"] += quantity
            to_customer_type_object["quantity"] += quantity
            customer_type_object["inventory"] -= quantity
            to_customer_type_object["min_qty"] = min_qty
            to_customer_type_object["max_qty"] = max_qty
            to_customer_type_object["regular"] = price

            return True, True
        to_customer_type_object["inventory"] = quantity
        to_customer_type_object["quantity"] = quantity
        customer_type_object["inventory"] -= quantity
        to_customer_type_object["min_qty"] = min_qty
        to_customer_type_object["max_qty"] = max_qty
        to_customer_type_object["regular"] = price
        return True, True
    except Exception:
        return False, "خطای سیستمی رخ داده است"


def edit_product_inventory(customer_type_object, quantity, min_qty,
                           max_qty):
    try:
        if quantity > customer_type_object["inventory"]:
            return False, "تعداد تخصیص داده شده بیشتر از موجودی می باشد"
        if quantity < customer_type_object["quantity"]:
            if customer_type_object["reserved"] > quantity:
            # if customer_type_object["quantity"] - customer_type_object["reserved"] < quantity:
                return False, "تغییر موجودی مجاز نمی باشد"
        customer_type_object["quantity"] = quantity
        customer_type_object["min_qty"] = min_qty
        customer_type_object["max_qty"] = max_qty

        return True, True

    except Exception:
        return False, "خطا در بروزرسانی"


def get_product_query(system_code):
    with MongoConnection() as mongo:
        product = mongo.product.find_one({"system_code": system_code})
    if not product:
        return False
    return product


def get_customer_type_object(product_object, storage_id, customer_type):
    qty_object = product_object.get("warehouse_details").get(customer_type).get("storages").get(storage_id)
    if not qty_object:
        return False
    return qty_object


def product_query(system_code, product_object):
    try:
        with MongoConnection() as mongo:
            mongo.product.replace_one({"system_code": system_code}, product_object)
        return True
    except:
        return False


def handle_cardex(qty_object,
                  storage_id,
                  system_code,
                  count,
                  staff_id,
                  staff_name,
                  service_name,
                  customer_type):
    try:
        quantity_cardex_data = {
            "staff_id": staff_id,
            "staff_user": staff_name,
            "incremental_id": "",
            "storage_id": storage_id,
            "stockName": "",
            "system_code": system_code,
            "sku": "",
            "type": service_name,
            "qty": count,
            "old_quantity": qty_object.get("quantity",0),
            "old_reserve": qty_object.get("reserved",0),
            "edit_date": str(jdatetime.datetime.now()).split(".")[0],
            "customer_type": customer_type,
            "old_inventory": qty_object.get("inventory",0),
            "biFlag": False
        }

        return quantity_cardex_data

    except Exception:
        return False


def cardex_query(quantity_cardex_data):
    try:
        with MongoConnection() as mongo:
            mongo.db.cardex.insert_one(quantity_cardex_data)
        return True
    except Exception:
        return False
