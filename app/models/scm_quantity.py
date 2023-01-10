import jdatetime

from app.helpers.mongo_connection import MongoConnection


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
                            "inventory": items['inventory'],
                            "unassigned": items['inventory'] - items['quantity'],

                        })

                        # cartegory changes
                        categorize[index_cat]['total_count'] += items['quantity']
                        categorize[index_cat]['total_price'] += items['price'] * items[
                            'quantity']
                        categorize[index_cat]['dailySales'] += items['dailySales']
                        categorize[index_cat]['unassigned'] += (items['inventory'] - items['quantity'])
                        categorize[index_cat]['inventory'] += items['inventory']

                        # sub categoriy changes
                        categorize[index_cat]['subCategories'][index_sub]['total_count'] += items['quantity']
                        categorize[index_cat]['subCategories'][index_sub]['total_price'] += items['price'] * items[
                            'quantity']
                        categorize[index_cat]['subCategories'][index_sub]['dailySales'] += items['dailySales']

                        # brand changes
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['total_count'] += \
                            items['quantity']
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['total_price'] += \
                            items['price'] * items['quantity']
                        categorize[index_cat]['subCategories'][index_sub]['brands'][index_brand]['dailySales'] += items[
                            'dailySales']

                        # model changes
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"][
                            index_model]['total_count'] += items['quantity']
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"][
                            index_model]['total_price'] += items['price'] * items['quantity']
                        categorize[index_cat]['subCategories'][index_sub]['brands'][index_brand]['models'][index_model][
                            'dailySales'] += items['dailySales']
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"][
                            index_model]['unassigned'] += (items['inventory'] - items['quantity'])
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"][
                            index_model]['inventory'] += items['inventory']

                    else:
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]["models"].append(
                            {
                                "model": items["model"],
                                "total_count": items['quantity'],
                                "total_price": items['price'],
                                "dailySales": items['dailySales'],
                                "inventory": items['inventory'],
                                "unassigned": items['inventory'] - items['quantity'],
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
                                        "inventory": items['inventory'],
                                        "unassigned": items['inventory'] - items['quantity'],

                                    }
                                ]
                            })

                        # catogory changes
                        categorize[index_cat]['total_count'] += items['quantity']
                        categorize[index_cat]['total_price'] += items['price'] * items['quantity']
                        categorize[index_cat]['dailySales'] += items['dailySales']
                        categorize[index_cat]['unassigned'] += (items['inventory'] - items['quantity'])
                        categorize[index_cat]['inventory'] += items['inventory']

                        # subcategory changes
                        categorize[index_cat]['subCategories'][index_sub]['total_count'] += items['quantity']
                        categorize[index_cat]['subCategories'][index_sub]['total_price'] += items['price'] * items[
                            'quantity']
                        categorize[index_cat]['subCategories'][index_sub]['dailySales'] += items['dailySales']

                        # brand changes
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['total_count'] += \
                            items['quantity']
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['total_price'] += \
                            items['price'] * items['quantity']
                        categorize[index_cat]['subCategories'][index_sub]['brands'][index_brand]['dailySales'] += items[
                            'dailySales']
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['unassigned'] += (
                                items['inventory'] - items['quantity'])
                        categorize[index_cat]["subCategories"][index_sub]['brands'][index_brand]['inventory'] += items[
                            'inventory']

                else:
                    categorize[index_cat]["subCategories"][index_sub]['brands'].append({
                        "brand": items["brand"],
                        "total_count": items['quantity'],
                        "total_price": items['price'],
                        "dailySales": items['dailySales'],
                        "inventory": items['inventory'],
                        "unassigned": items['inventory'] - items['quantity'],
                        "models": [
                            {
                                "model": items["model"],
                                "total_count": items['quantity'],
                                "total_price": items['price'],
                                "dailySales": items['dailySales'],
                                "inventory": items['inventory'],
                                "unassigned": items['inventory'] - items['quantity'],
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
                                        "inventory": items['inventory'],
                                        "unassigned": items['inventory'] - items['quantity'],

                                    }
                                ]
                            }
                        ]
                    })
                    # category changes
                    categorize[index_cat]['total_count'] += items['quantity']
                    categorize[index_cat]['total_price'] += items['price'] * items[
                        'quantity']
                    categorize[index_cat]['dailySales'] += items['dailySales']
                    categorize[index_cat]['unassigned'] += (items['inventory'] - items['quantity'])
                    categorize[index_cat]['inventory'] += items['inventory']

                    # subcatogory changes
                    categorize[index_cat]['subCategories'][index_sub]['total_count'] += items['quantity']
                    categorize[index_cat]['subCategories'][index_sub]['total_price'] += items['price'] * items[
                        'quantity']
                    categorize[index_cat]['subCategories'][index_sub]['dailySales'] += items['dailySales']
                    categorize[index_cat]['subCategories'][index_sub]['unassigned'] += (
                            items['inventory'] - items['quantity'])
                    categorize[index_cat]['subCategories'][index_sub]['inventory'] += items['inventory']


            else:
                categorize[index_cat]["subCategories"].append({
                    "subCategory": items['subCat'],
                    "total_count": items['quantity'],
                    "total_price": items['price'],
                    "dailySales": items['dailySales'],
                    "inventory": items['inventory'],
                    "unassigned": items['inventory'] - items['quantity'],
                    "brands": [
                        {
                            "brand": items["brand"],
                            "total_count": items['quantity'],
                            "total_price": items['price'],
                            "dailySales": items['dailySales'],
                            "inventory": items['inventory'],
                            "unassigned": items['inventory'] - items['quantity'],
                            "models": [
                                {
                                    "model": items["model"],
                                    "total_count": items['quantity'],
                                    "total_price": items['price'],
                                    "dailySales": items['dailySales'],
                                    "inventory": items['inventory'],
                                    "unassigned": items['inventory'] - items['quantity'],
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
                                            "inventory": items['inventory'],
                                            "unassigned": items['inventory'] - items['quantity'],

                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                })

                # category changes
                categorize[index_cat]['total_count'] += items['quantity']
                categorize[index_cat]['total_price'] += items['price'] * items[
                    'quantity']
                categorize[index_cat]['dailySales'] += items['dailySales']
                categorize[index_cat]['unassigned'] += (items['inventory'] - items['quantity'])
                categorize[index_cat]['inventory'] += items['inventory']
        else:
            categorize.append({
                "category": items["cat"],
                "total_count": items['quantity'],
                "total_price": items['price'],
                "dailySales": items['dailySales'],
                "inventory": items['inventory'],
                "unassigned": items['inventory'] - items['quantity'],
                "subCategories": [{
                    "subCategory": items['subCat'],
                    "total_count": items['quantity'],
                    "total_price": items['price'],
                    "dailySales": items['dailySales'],
                    "inventory": items['inventory'],
                    "unassigned": items['inventory'] - items['quantity'],
                    "brands": [
                        {
                            "brand": items["brand"],
                            "total_count": items['quantity'],
                            "total_price": items['price'],
                            "dailySales": items['dailySales'],
                            "inventory": items['inventory'],
                            "unassigned": items['inventory'] - items['quantity'],
                            "models": [
                                {
                                    "model": items["model"],
                                    "total_count": items['quantity'],
                                    "total_price": items['price'],
                                    "dailySales": items['dailySales'],
                                    "inventory": items['inventory'],
                                    "unassigned": items['inventory'] - items['quantity'],
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
                                            "inventory": items['inventory'],
                                            "unassigned": items['inventory'] - items['quantity'],
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
                        try:
                            for storage_key, storage_value, in value['storages'].items():
                                if storage_value['storage_id'] in storages:
                                    if storage_value.get('quantity') is not None and storage_value.get(
                                            'quantity') > 0:
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
                                            "inventory": storage_value['inventory'],
                                            "customer_type": key
                                        })
                                    else:
                                        pass
                        except:
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
            return False, "محصولی با نوع مشتری ویا کد انبار مورد نظر یافت نشد"
        return True, customer_type_object
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
            return False, "محصولی با نوع مشتری ویا کد انبار مورد نظر یافت نشد"

        if transfer:
            to_customer_type_object = get_customer_type_object(product_object, storage_id, to_customer_type)
            if not to_customer_type_object:
                return False, "محصولی با نوع مشتری ویا کد انبار مورد نظر یافت نشد"
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
        to_customer_type_object["reserved"] = 0
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
    qty_object = product_object.get("warehouse_details", {}).get(customer_type, {}).get("storages", {}).get(storage_id,
                                                                                                            {})
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
            "old_quantity": qty_object.get("quantity", 0),
            "old_reserve": qty_object.get("reserved", 0),
            "edit_date": str(jdatetime.datetime.now()).split(".")[0],
            "customer_type": customer_type,
            "old_inventory": qty_object.get("inventory", 0),
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


def moghayerat_report():
    with MongoConnection() as mongo:

        storage_sys = []
        archive_result = []
        archives = mongo.archive.find()
        for root_archive in archives:
            for articles_archive in root_archive["articles"]:
                if articles_archive["exist"]:
                    if {"system_code": root_archive["system_code"],
                        "storage": articles_archive["stockId"]} not in storage_sys:
                        storage_sys.append(
                            {"system_code": root_archive["system_code"], "storage": articles_archive["stockId"]})
                        archive_result.append({
                            "s_c": root_archive["system_code"],
                            "storage": articles_archive["stockId"],
                            "archive_c": 1,
                            "imeis": [{"imei": articles_archive["first"]}]
                        })
                    else:
                        index = storage_sys.index(
                            {"system_code": root_archive["system_code"], "storage": articles_archive["stockId"]})
                        archive_result[index]["archive_c"] += 1
                        archive_result[index]["imeis"].append({"imei": articles_archive["first"]})

        """
        check archive with imeis
        """

        for cursor_moghayerat in archive_result:
            imeis = mongo.imeis.find_one(
                {"system_code": cursor_moghayerat["s_c"], "storage_id": cursor_moghayerat["storage"]})
            cursor_moghayerat["imeis_c"] = len(imeis["imeis"])

            product = mongo.product.find_one({"system_code": cursor_moghayerat["s_c"]})
            for key, val in product["warehouse_details"].items():
                if val is not None:
                    if val.get("storages") is not None:
                        for k, v in val["storages"].items():
                            if k == cursor_moghayerat["storage"]:
                                if v.get("quantity") is not None:

                                    if cursor_moghayerat.get("product_c") is None:
                                        cursor_moghayerat["product_c"] = v["quantity"]
                                        cursor_moghayerat["imeis_c"] = len(imeis["imeis"])
                                    else:
                                        cursor_moghayerat["product_c"] += v["quantity"]

        """
        moghayerat with products
        """

        moghayerat = []

        for items in archive_result:
            if items["imeis_c"] == items["product_c"] and items["imeis_c"] == items["product_c"] and items[
                "imeis_c"] == items[
                "archive_c"]:
                pass
            else:
                del items["imeis"]
                moghayerat.append(items)
        return moghayerat


def management_reports():
    with MongoConnection() as mongo:
        inv_warehouse_report = list(mongo.product.aggregate([
            {
                '$addFields': {
                    'B2B': '$warehouse_details.B2B.storages'
                }
            }, {
                '$match': {
                    'main_category': 'Device'
                }
            }, {
                '$project': {
                    'brand': '$brand',
                    'result': {
                        '$objectToArray': '$B2B'
                    }
                }
            }, {
                '$unwind': '$result'
            }, {
                '$addFields': {
                    'res': '$result.v',
                    'price': '$result.v.regular'
                }
            }, {
                '$match': {
                    'res.quantity': {
                        '$gt': 0
                    }
                }
            }, {
                '$project': {
                    '_id': 0,
                    'brand': 1,
                    'totalPrice': {
                        '$multiply': [
                            '$price', '$res.quantity'
                        ]
                    },
                    'res': 1
                }
            }, {
                '$group': {
                    '_id': {
                        'brand': '$brand',
                        'warehouse': '$res.warehouse_label',
                        'storage_id': '$res.storage_id'
                    },
                    'totalQty': {
                        '$sum': '$res.quantity'
                    },
                    'totalPrice': {
                        '$sum': '$totalPrice'
                    }
                }
            }, {
                '$project': {
                    'storage': '$_id.warehouse',
                    'brand': '$_id.brand',
                    '_id': 0,
                    'totalQty': 1,
                    'totalPrice': 1,
                    'storageId': '$_id.storage_id'
                }
            }
        ]))

        def custom_sort(k):
            return int(k['storageId'])

        inv_warehouse_report.sort(key=custom_sort)
        inv_warehouse_sidebar_total_qty = 0
        inv_warehouse_sidebar_total_price = 0
        inv_brand_sidebar = {}
        if inv_warehouse_report:
            storages = []
            result_inv_warehouse_report = []
            for items in inv_warehouse_report:
                if items['storage'] not in storages:
                    result_inv_warehouse_report.append({"storage": items['storage'], "data": [items]})
                    storages.append(items['storage'])
                else:
                    index = storages.index(items['storage'])
                    result_inv_warehouse_report[index]['data'].append(items)
                inv_warehouse_sidebar_total_qty += items['totalQty']
                inv_warehouse_sidebar_total_price += items['totalPrice']
            inv_brand_sidebar = {"totalQty": inv_warehouse_sidebar_total_qty,
                                 "totalPrice": inv_warehouse_sidebar_total_price}

        brand_report = list(mongo.product.aggregate([
            {
                '$addFields': {
                    'B2B': '$warehouse_details.B2B.storages'
                }
            }, {
                '$match': {
                    'main_category': 'Device'
                }
            }, {
                '$project': {
                    'brand': '$brand',
                    'result': {
                        '$objectToArray': '$B2B'
                    }
                }
            }, {
                '$unwind': '$result'
            }, {
                '$addFields': {
                    'res': '$result.v',
                    'price': '$result.v.regular'
                }
            }, {
                '$match': {
                    'res.quantity': {
                        '$gt': 0
                    }
                }
            }, {
                '$project': {
                    '_id': 0,
                    'brand': 1,
                    'totalPrice': {
                        '$multiply': [
                            '$price', '$res.quantity'
                        ]
                    },
                    'res': 1
                }
            }, {
                '$group': {
                    '_id': '$brand',
                    'totalQty': {
                        '$sum': '$res.quantity'
                    },
                    'totalPrice': {
                        '$sum': '$totalPrice'
                    }
                }
            }, {
                '$project': {
                    'brand': '$_id',
                    '_id': 0,
                    'totalQty': 1,
                    'totalPrice': 1
                }
            }
        ]))
        brand_sidebar_total_qty = 0
        brand_sidebar_total_price = 0
        brand_sidebar = {}
        if brand_report:
            brand_report_brands = []
            result_brand_report = []
            for items in brand_report:
                if items['brand'] not in brand_report_brands:
                    result_brand_report.append({"brand": items['brand'], "data": [items]})
                    brand_report_brands.append(items['brand'])
                else:
                    index = brand_report_brands.index(items['brand'])
                    result_brand_report[index]['data'].append(items)
                brand_sidebar_total_qty += items['totalQty']
                brand_sidebar_total_price += items['totalPrice']
            brand_sidebar = {"totalQty": brand_sidebar_total_qty, "totalPrice": brand_sidebar_total_price}

        transfer_report = list(mongo.imeis.aggregate([
            {
                '$match': {
                    'storage_id': '1000'
                }
            }, {
                '$unwind': '$imeis'
            }, {
                '$group': {
                    '_id': {
                        'to_storage': '$imeis.to_storage',
                        'brand': '$brand'
                    },
                    'fieldN': {
                        '$push': '$imeis'
                    }
                }
            }, {
                '$project': {
                    'brand': '$_id.brand',
                    'toStorage': '$_id.to_storage',
                    'count': {
                        '$size': '$fieldN'
                    },
                    '_id': 0
                }
            }
        ]))
        if transfer_report:
            def custom_sort(k):
                return int(k['toStorage'])

            transfer_report.sort(key=custom_sort)
            transfer_array = []
            for items in transfer_report:

                items['toStorage'] = mongo.warehouses.find_one({"warehouse_id": int(items['toStorage'])},
                                                               {"warehouse_name": True, "_id": False}).get(
                    'warehouse_name')
                if items['toStorage'] not in transfer_array:
                    transfer_array.append(items['toStorage'])
        return {"invBrandReport": result_inv_warehouse_report, "invBrandSide": inv_brand_sidebar,
                "brandReport": result_brand_report,
                "brandSide": brand_sidebar, "storageNames": storages, "brands": brand_report_brands,
                "transferReport": transfer_report, "transferStorages": transfer_array
                }

        # return transfer_report


# print(moghayerat_report())
