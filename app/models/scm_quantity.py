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
            query['systemCode'] = system_code
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


inv_report(["1"], None, None,[{'systemCode': '2000010020015002001026002', 'stockId': '1'},
                                                {'systemCode': '2000010020015002001024002', 'stockId': '1'},
                                                {'systemCode': '2000010020015002001021002', 'stockId': '1'},
                                                {'systemCode': '2000010020018003001021001', 'stockId': '1'},
                                                {'systemCode': '2000010030001001001001002', 'stockId': '1'},
                                                {'systemCode': '2000010030002001001003002', 'stockId': '1'},
                                                {'systemCode': '2000010030003001001001002', 'stockId': '1'},
                                                {'systemCode': '2000010050009002001001001', 'stockId': '1'},
                                                {'systemCode': '2000010010005006001001001', 'stockId': '1'},
                                                {'systemCode': '2000010010007002001001001', 'stockId': '1'},
                                                {'systemCode': '2000010010029002001095002', 'stockId': '1'},
                                                {'systemCode': '2000010020022003001021001', 'stockId': '2'},
                                                {'systemCode': '2000010020017003001021001', 'stockId': '2'},
                                                {'systemCode': '2000010020017003001022001', 'stockId': '2'},
                                                {'systemCode': '2000010020017003001022001', 'stockId': '8'},
                                                {'systemCode': '2000010010004003001059001', 'stockId': '2'},
                                                {'systemCode': '2000010010004003001059002', 'stockId': '2'},
                                                {'systemCode': '2000010010004003001100001', 'stockId': '2'},
                                                {'systemCode': '2000010010004003001008001', 'stockId': '2'},
                                                {'systemCode': '2000010010013003001001002', 'stockId': '1'},
                                                {'systemCode': '2000010010012001001001002', 'stockId': '1'},
                                                {'systemCode': '2000010010031001001108001', 'stockId': '1'},
                                                {'systemCode': '2000010030005001001001002', 'stockId': '1'},
                                                {'systemCode': '2000010010012002001001001', 'stockId': '1'},
                                                {'systemCode': '2000010020014003001076002', 'stockId': '1'},
                                                {'systemCode': '2000010010003009001001001', 'stockId': '1'},
                                                {'systemCode': '2000010010007004001001002', 'stockId': '1'},
                                                {'systemCode': '2000010010011002001001001', 'stockId': '1'},
                                                {'systemCode': '2000010020004001001021001', 'stockId': '1'},
                                                {'systemCode': '2000010020017003001021002', 'stockId': '1'},
                                                {'systemCode': '2000010050009002001005001', 'stockId': '1'},
                                                {'systemCode': '2000010010030002001001002', 'stockId': '3'},
                                                {'systemCode': '2000010010030001001001002', 'stockId': '3'},
                                                {'systemCode': '2000010010011003001001002', 'stockId': '3'},
                                                {'systemCode': '2000010020008001001006001', 'stockId': '3'},
                                                {'systemCode': '2000010020015002001026002', 'stockId': '3'},
                                                {'systemCode': '2000010020017003001021001', 'stockId': '3'},
                                                {'systemCode': '2000010050009002001001001', 'stockId': '7'},
                                                {'systemCode': '2000010020022003001021001', 'stockId': '7'},
                                                {'systemCode': '2000010010005006001005001', 'stockId': '1'},
                                                {'systemCode': '2000010020004001001021001', 'stockId': '8'},
                                                {'systemCode': '2000010010030001001016002', 'stockId': '8'},
                                                {'systemCode': '2000010010012002001013001', 'stockId': '1'},
                                                {'systemCode': '2000010050009001001001002', 'stockId': '3'},
                                                {'systemCode': '2000010050006002001030002', 'stockId': '3'},
                                                {'systemCode': '2000010010017001001003002', 'stockId': '1'},
                                                {'systemCode': '2000010010010007001016002', 'stockId': '10'},
                                                {'systemCode': '2000010010010007001003002', 'stockId': '10'},
                                                {'systemCode': '2000010050009001001001002', 'stockId': '7'},
                                                {'systemCode': '2000010010030001001016002', 'stockId': '2'},
                                                {'systemCode': '2000010010010007001003002', 'stockId': '2'},
                                                {'systemCode': '2000010020004001001021001', 'stockId': '2'},
                                                {'systemCode': '2000010050009001001001002', 'stockId': '2'},
                                                {'systemCode': '2000010010013002001016002', 'stockId': '1'},
                                                {'systemCode': '2000010020017003001021001', 'stockId': '7'},
                                                {'systemCode': '2000010050001004001043002', 'stockId': '7'},
                                                {'systemCode': '2000010020027001001089002', 'stockId': '7'},
                                                {'systemCode': '2000010020008003001103001', 'stockId': '7'},
                                                {'systemCode': '2000010020024001001096002', 'stockId': '1'},
                                                {'systemCode': '2000010020027003001089001', 'stockId': '3'},
                                                {'systemCode': '2000010020027003001089001', 'stockId': '10'},
                                                {'systemCode': '2000010020008001001104002', 'stockId': '1'},
                                                {'systemCode': '2000010010030001001001002', 'stockId': '2'},
                                                {'systemCode': '2000010010018002001001001', 'stockId': '1'},
                                                {'systemCode': '2000010010004003001100001', 'stockId': '1'},
                                                {'systemCode': '2000010010011002001016001', 'stockId': '1'},
                                                {'systemCode': '2000010020008001001104001', 'stockId': '1'},
                                                {'systemCode': '2000010010004003001100001', 'stockId': '10'},
                                                {'systemCode': '2000010020008001001104001', 'stockId': '10'},
                                                {'systemCode': '2000010020004001001021001', 'stockId': '10'},
                                                {'systemCode': '2000010050001004001043002', 'stockId': '2'},
                                                {'systemCode': '2000010050009002001001001', 'stockId': '2'},
                                                {'systemCode': '2000010010030001001005002', 'stockId': '2'},
                                                {'systemCode': '2000010020008003001103001', 'stockId': '2'},
                                                {'systemCode': '2000010010010007001003002', 'stockId': '1'},
                                                {'systemCode': '2000010020008003001103001', 'stockId': '1'},
                                                {'systemCode': '2000010010004003001059001', 'stockId': '1'},
                                                {'systemCode': '2000010010015002001001001', 'stockId': '1'},
                                                {'systemCode': '2000010020022003001021001', 'stockId': '1'},
                                                {'systemCode': '2000010020004001001021001', 'stockId': '9'},
                                                {'systemCode': '2000010020003006001052002', 'stockId': '9'},
                                                {'systemCode': '2000010010005006001001001', 'stockId': '9'},
                                                {'systemCode': '2000010020008001001104001', 'stockId': '7'},
                                                {'systemCode': '2000010010005005001001001', 'stockId': '1'},
                                                {'systemCode': '2000010010011003001001001', 'stockId': '1'},
                                                {'systemCode': '2000010020027003001089001', 'stockId': '1'},
                                                {'systemCode': '2000010050001004001042002', 'stockId': '1'},
                                                {'systemCode': '2000010050009002001005002', 'stockId': '1'},
                                                {'systemCode': '2000010010005005001005001', 'stockId': '1'},
                                                {'systemCode': '2000010020008003001101001', 'stockId': '2'},
                                                {'systemCode': '2000010010015004001001001', 'stockId': '2'},
                                                {'systemCode': '2000010020004001001021001', 'stockId': '7'},
                                                {'systemCode': '2000010010030001001001002', 'stockId': '7'},
                                                {'systemCode': '2000010020003006001111002', 'stockId': '1'}], [{'systemCode': '2000010020015002001026002', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010020015002001024002', 'count': 6, 'stockId': '1'},
                           {'systemCode': '2000010020015002001021002', 'count': 16, 'stockId': '1'},
                           {'systemCode': '2000010020018003001021001', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010030001001001001002', 'count': 22, 'stockId': '1'},
                           {'systemCode': '2000010030002001001003002', 'count': 13, 'stockId': '1'},
                           {'systemCode': '2000010030003001001001002', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010050009002001001001', 'count': 5, 'stockId': '1'},
                           {'systemCode': '2000010010005006001001001', 'count': 7, 'stockId': '1'},
                           {'systemCode': '2000010010007002001001001', 'count': 15, 'stockId': '1'},
                           {'systemCode': '2000010010029002001095002', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010020022003001021001', 'count': 3, 'stockId': '2'},
                           {'systemCode': '2000010020017003001021001', 'count': 5, 'stockId': '2'},
                           {'systemCode': '2000010020017003001022001', 'count': 5, 'stockId': '2'},
                           {'systemCode': '2000010020017003001022001', 'count': 2, 'stockId': '8'},
                           {'systemCode': '2000010010004003001059001', 'count': 5, 'stockId': '2'},
                           {'systemCode': '2000010010004003001059002', 'count': 2, 'stockId': '2'},
                           {'systemCode': '2000010010004003001100001', 'count': 1, 'stockId': '2'},
                           {'systemCode': '2000010010004003001008001', 'count': 2, 'stockId': '2'},
                           {'systemCode': '2000010010013003001001002', 'count': 4, 'stockId': '1'},
                           {'systemCode': '2000010010012001001001002', 'count': 3, 'stockId': '1'},
                           {'systemCode': '2000010010031001001108001', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010030005001001001002', 'count': 4, 'stockId': '1'},
                           {'systemCode': '2000010010012002001001001', 'count': 5, 'stockId': '1'},
                           {'systemCode': '2000010020014003001076002', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010010003009001001001', 'count': 3, 'stockId': '1'},
                           {'systemCode': '2000010010007004001001002', 'count': 5, 'stockId': '1'},
                           {'systemCode': '2000010010011002001001001', 'count': 5, 'stockId': '1'},
                           {'systemCode': '2000010020004001001021001', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010020017003001021002', 'count': 9, 'stockId': '1'},
                           {'systemCode': '2000010050009002001005001', 'count': 4, 'stockId': '1'},
                           {'systemCode': '2000010010030002001001002', 'count': 1, 'stockId': '3'},
                           {'systemCode': '2000010010030001001001002', 'count': 2, 'stockId': '3'},
                           {'systemCode': '2000010010011003001001002', 'count': 1, 'stockId': '3'},
                           {'systemCode': '2000010020008001001006001', 'count': 1, 'stockId': '3'},
                           {'systemCode': '2000010020015002001026002', 'count': 1, 'stockId': '3'},
                           {'systemCode': '2000010020017003001021001', 'count': 1, 'stockId': '3'},
                           {'systemCode': '2000010050009002001001001', 'count': 5, 'stockId': '7'},
                           {'systemCode': '2000010020022003001021001', 'count': 3, 'stockId': '7'},
                           {'systemCode': '2000010010005006001005001', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010020004001001021001', 'count': 1, 'stockId': '8'},
                           {'systemCode': '2000010010030001001016002', 'count': 1, 'stockId': '8'},
                           {'systemCode': '2000010010012002001013001', 'count': 4, 'stockId': '1'},
                           {'systemCode': '2000010050009001001001002', 'count': 1, 'stockId': '3'},
                           {'systemCode': '2000010050006002001030002', 'count': 1, 'stockId': '3'},
                           {'systemCode': '2000010010017001001003002', 'count': 4, 'stockId': '1'},
                           {'systemCode': '2000010010010007001016002', 'count': 1, 'stockId': '10'},
                           {'systemCode': '2000010010010007001003002', 'count': 1, 'stockId': '10'},
                           {'systemCode': '2000010050009001001001002', 'count': 1, 'stockId': '7'},
                           {'systemCode': '2000010010030001001016002', 'count': 2, 'stockId': '2'},
                           {'systemCode': '2000010010010007001003002', 'count': 4, 'stockId': '2'},
                           {'systemCode': '2000010020004001001021001', 'count': 5, 'stockId': '2'},
                           {'systemCode': '2000010050009001001001002', 'count': 4, 'stockId': '2'},
                           {'systemCode': '2000010010013002001016002', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010020017003001021001', 'count': 2, 'stockId': '7'},
                           {'systemCode': '2000010050001004001043002', 'count': 1, 'stockId': '7'},
                           {'systemCode': '2000010020027001001089002', 'count': 1, 'stockId': '7'},
                           {'systemCode': '2000010020008003001103001', 'count': 1, 'stockId': '7'},
                           {'systemCode': '2000010020024001001096002', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010020027003001089001', 'count': 1, 'stockId': '3'},
                           {'systemCode': '2000010020027003001089001', 'count': 1, 'stockId': '10'},
                           {'systemCode': '2000010020008001001104002', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010010030001001001002', 'count': 4, 'stockId': '2'},
                           {'systemCode': '2000010010018002001001001', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010010004003001100001', 'count': 3, 'stockId': '1'},
                           {'systemCode': '2000010010011002001016001', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010020008001001104001', 'count': 4, 'stockId': '1'},
                           {'systemCode': '2000010010004003001100001', 'count': 1, 'stockId': '10'},
                           {'systemCode': '2000010020008001001104001', 'count': 1, 'stockId': '10'},
                           {'systemCode': '2000010020004001001021001', 'count': 1, 'stockId': '10'},
                           {'systemCode': '2000010050001004001043002', 'count': 2, 'stockId': '2'},
                           {'systemCode': '2000010050009002001001001', 'count': 3, 'stockId': '2'},
                           {'systemCode': '2000010010030001001005002', 'count': 2, 'stockId': '2'},
                           {'systemCode': '2000010020008003001103001', 'count': 2, 'stockId': '2'},
                           {'systemCode': '2000010010010007001003002', 'count': 4, 'stockId': '1'},
                           {'systemCode': '2000010020008003001103001', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010010004003001059001', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010010015002001001001', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010020022003001021001', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010020004001001021001', 'count': 1, 'stockId': '9'},
                           {'systemCode': '2000010020003006001052002', 'count': 1, 'stockId': '9'},
                           {'systemCode': '2000010010005006001001001', 'count': 1, 'stockId': '9'},
                           {'systemCode': '2000010020008001001104001', 'count': 1, 'stockId': '7'},
                           {'systemCode': '2000010010005005001001001', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010010011003001001001', 'count': 2, 'stockId': '1'},
                           {'systemCode': '2000010020027003001089001', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010050001004001042002', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010050009002001005002', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010010005005001005001', 'count': 1, 'stockId': '1'},
                           {'systemCode': '2000010020008003001101001', 'count': 2, 'stockId': '2'},
                           {'systemCode': '2000010010015004001001001', 'count': 1, 'stockId': '2'},
                           {'systemCode': '2000010020004001001021001', 'count': 1, 'stockId': '7'},
                           {'systemCode': '2000010010030001001001002', 'count': 1, 'stockId': '7'},
                           {'systemCode': '2000010020003006001111002', 'count': 1, 'stockId': '1'}])
