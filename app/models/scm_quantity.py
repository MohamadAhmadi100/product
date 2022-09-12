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
                        categorize[index_cat]['dailySales'] += items['dailySales']
                        categorize[index_cat]['subCategories'][index_sub]['total_count'] += items['quantity']
                        categorize[index_cat]['subCategories'][index_sub]['total_price'] += items['price'] * items[
                            'quantity']
                        categorize[index_cat]['subCategories'][index_sub]['dailySales'] += items['dailySales']
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
                        categorize[index_cat]['dailySales'] += items['dailySales']
                        categorize[index_cat]['subCategories'][index_sub]['total_count'] += items['quantity']
                        categorize[index_cat]['subCategories'][index_sub]['total_price'] += items['price'] * items[
                            'quantity']
                        categorize[index_cat]['subCategories'][index_sub]['dailySales'] += items['dailySales']

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
                    categorize[index_cat]['dailySales'] += items['dailySales']
                    categorize[index_cat]['subCategories'][index_sub]['total_count'] += items['quantity']
                    categorize[index_cat]['subCategories'][index_sub]['total_price'] += items['price'] * items[
                        'quantity']
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
                                if storage_value['quantity'] > 0:
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
        # build object for response
        result_categorize = categorized_data(result)

        return {"success": True, "result": result_categorize, "status_code": 200}


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
