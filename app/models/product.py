import math
import re
from copy import copy
from typing import Union

import jdatetime

from app.helpers.mongo_connection import MongoConnection
from app.helpers.redis_connection import RedisConnection
from app.models.kowsar import KowsarGetter
# from app.validators.attribute_validator import attribute_validator
from app.reserve_quantity.check_quantity import check_quantity


class Product:
    def __init__(self, name, url_name, system_codes):
        self.products = None
        self.name = name
        self.url_name = url_name
        self.system_codes = system_codes

    def system_codes_are_unique(self):
        with MongoConnection() as mongo:
            return mongo.product.count_documents({"system_code": {"$in": self.system_codes}}) == 0

    @staticmethod
    def change_visibility(system_code, customer_type, value):
        with MongoConnection() as mongo:
            result = mongo.product.update_one(
                {"system_code": system_code},
                {"$set": {f"visible_in_site.{customer_type}": value}}
            )
            if result.modified_count:
                return True
            return False

    @staticmethod
    def torob(page, system_code, page_url, return_all=False):
        with MongoConnection() as mongo:
            skip = (page - 1) * 100
            query = {}
            if system_code:
                query['system_code'] = {"$regex": "^" + system_code}
                skip = 0
            elif page_url:
                page_url = page_url if not page_url[-1] == "/" else page_url[:-1]
                query['system_code'] = {"$regex": "^" + page_url.split("/")[-1]}
                skip = 0
            pipe_lines = [
                {"$match": query},
                {"$sort": {
                    "system_code": 1
                }
                },
                {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$system_code', 0, 16
                            ]
                        },
                        'data': {
                            '$first': {
                                'image_link': '$attributes.mainImage-pd',
                                'image_links': [
                                    '$attributes.mainImage-pd', '$attributes.otherImage-pd', '$attributes.closeImage-pd'
                                ],
                                'page_url': {
                                    '$concat': [
                                        'https://rakiano.com/product/', {
                                            '$substr': [
                                                '$system_code', 0, 16
                                            ]
                                        }
                                    ]
                                },
                                'title': '$name',
                                'spec': '$configs',
                                'category_name': '$sub_category',
                                'date': '$date'
                            }
                        },
                        'storages': {
                            '$push': {
                                '$objectToArray': '$warehouse_details.B2C.storages'
                            }
                        }
                    }
                }, {
                    '$addFields': {
                        'storages': {
                            '$reduce': {
                                'input': '$storages',
                                'initialValue': [],
                                'in': {
                                    '$concatArrays': ["$$value", "$$this.v"]
                                }
                            }
                        }
                    }
                }, {
                    '$sort': {
                        'data.date': -1
                    }
                }, {
                    '$facet': {
                        'products': [
                            {
                                '$replaceRoot': {
                                    'newRoot': {
                                        '$mergeObjects': [
                                            '$data', {
                                                'page_unique': '$_id'
                                            }, {
                                                'storages': '$storages'
                                            }
                                        ]
                                    }
                                }
                            }, {
                                '$project': {
                                    'date': 0
                                }
                            }, {
                                '$skip': skip
                            }, {
                                '$limit': 100
                            }
                        ],
                        'count': [
                            {
                                '$count': 'count'
                            }
                        ]
                    }
                }
            ]
            if return_all:
                del pipe_lines[0]
                del pipe_lines[-1]['$facet']['products'][-2:]
            data = mongo.product.aggregate(pipe_lines)
            data = data.next()
            counts = data['count'][0]['count']
            data = data["products"]
            data_list = list()
            for i in data:
                old_price = 0
                current_price = 0
                availability = None
                for storage in i['storages']:
                    if (storage.get('quantity', 0) - storage.get('reserved', 0) - storage.get('min_qty', 1)) >= 0:
                        availability = "instock"
                        if storage.get('special') and (
                                jdatetime.datetime.strptime(
                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                                >
                                jdatetime.datetime.strptime(storage.get("special_to_date", jdatetime.datetime.now(
                                ).strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S")
                        ):
                            if current_price > storage.get('special') or current_price == 0:
                                current_price = storage.get('special')
                                old_price = storage.get("regular")
                        else:
                            if current_price > storage.get('regular') or current_price == 0:
                                current_price = storage.get("regular")

                del i['storages']
                data_list.append(dict(i, **({"availability": availability,
                                             "current_price": current_price,
                                             } if not old_price else {"availability": availability,
                                                                      "current_price": current_price,
                                                                      "old_price": old_price})))
        return {"products": data_list, "count": counts, "max_pages": math.ceil(counts / 100)}

    @staticmethod
    def main_menu(customer_type, user_allowed_storages):
        with MongoConnection() as mongo:
            result = mongo.product.aggregate([
                {
                    '$match': {
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'min_qty': '$zz.v.min_qty',
                        'max_qty': {
                            '$cond': [
                                {
                                    '$gt': [
                                        {
                                            '$subtract': [
                                                '$zz.v.quantity', '$zz.v.reserved'
                                            ]
                                        }, '$zz.v.max_qty'
                                    ]
                                }, '$zz.v.max_qty', {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }
                            ]
                        },
                        'regular': '$zz.v.regular',
                        'special': {
                            '$cond': [
                                {
                                    '$and': [
                                        {
                                            '$gt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_from_date'
                                            ]
                                        }, {
                                            '$lt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_to_date'
                                            ]
                                        }
                                    ]
                                }, '$zz.v.special', None
                            ]
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': dict({
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }
                    }, **({} if not user_allowed_storages else {
                        "storage_id": {"$in": user_allowed_storages}}))
                }, {
                    '$group': {
                        '_id': '$_id',
                        'item': {
                            '$addToSet': '$root_obj'
                        },
                        'prices': {
                            '$addToSet': {
                                'storage_id': '$storage_id',
                                'regular': '$regular',
                                'special': '$special'
                            }
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'item': {
                            '$first': '$item'
                        },
                        'prices': 1
                    }
                }, {
                    '$project': {
                        'system_code': '$item.system_code',
                        'name': '$item.name',
                        'color': '$item.color',
                        'attributes': '$item.attributes',
                        'sub_category': '$item.sub_category',
                        'brand': '$item.brand',
                        'prices': 1
                    }
                },
                {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$system_code', 0, 16
                            ]
                        },
                        'name': {
                            '$first': '$name'
                        },
                        'products': {
                            '$push': '$$ROOT'
                        },
                        'prices': {
                            '$push': {
                                'system_code': '$system_code',
                                'prices': '$prices'
                            }
                        },
                        'sub_category': {
                            '$addToSet': '$sub_category'
                        },
                        'brand': {
                            '$addToSet': '$brand'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'products': 1,
                        'name': 1,
                        'system_code': '$_id',
                        'color': {
                            '$setIntersection': {
                                '$reduce': {
                                    'input': '$products',
                                    'initialValue': [],
                                    'in': {
                                        '$concatArrays': [
                                            '$$value', [
                                                '$$this.color'
                                            ]
                                        ]
                                    }
                                }
                            }
                        },
                        'images': {
                            '$setIntersection': {
                                '$reduce': {
                                    'input': '$products',
                                    'initialValue': [],
                                    'in': {
                                        '$concatArrays': [
                                            '$$value', [
                                                '$$this.attributes.mainImage-pd'
                                            ]
                                        ]
                                    }
                                }
                            }
                        },
                        'prices': 1,
                        'sub_category': {
                            '$first': '$sub_category'
                        },
                        'brand': {
                            '$first': '$brand'
                        }
                    }
                }, {
                    '$facet': {
                        'mobiles': [
                            {
                                '$match': {
                                    'sub_category': 'Mobile'
                                }
                            }, {
                                '$group': {
                                    '_id': '$brand',
                                    'products': {
                                        '$push': {
                                            'name': '$name',
                                            'prices': '$prices',
                                            'system_code': '$system_code',
                                            'color': '$color',
                                            'images': '$images'
                                        }
                                    },
                                    "system_code": {
                                        "$first": {"$substr": ["$system_code", 0, 9]}
                                    },
                                    "sys_codes": {"$push": "$system_code"}
                                }
                            }, {
                                '$project': {
                                    'products': {
                                        '$slice': [
                                            '$products', 10
                                        ]
                                    },
                                    "system_code": 1,
                                    "sys_codes": {"$first": "$sys_codes"},
                                    'name': '$_id',
                                    '_id': 0
                                }
                            },
                            {
                                "$sort": {"sys_codes": 1}
                            }, {"$project": {"sys_codes": 0}}
                        ],
                        'others': [
                            {
                                '$match': {
                                    'sub_category': {
                                        '$ne': 'Mobile'
                                    }
                                }
                            }, {
                                '$group': {
                                    '_id': '$sub_category',
                                    "system_code": {
                                        "$first": {"$substr": ["$system_code", 0, 6]}
                                    },
                                    'products': {
                                        '$push': {
                                            'name': '$name',
                                            'prices': '$prices',
                                            'system_code': '$system_code',
                                            'color': '$color',
                                            'images': '$images'
                                        }
                                    }
                                }
                            }, {
                                '$project': {
                                    'products': {
                                        '$slice': [
                                            '$products', 10
                                        ]
                                    },
                                    "system_code": 1,
                                    'name': '$_id',
                                    '_id': 0
                                }
                            }
                        ]
                    }
                }, {
                    '$project': {
                        'data': {
                            '$concatArrays': [
                                '$mobiles', '$others'
                            ]
                        }
                    }
                }
            ])
            brands = mongo.product.aggregate([
                {
                    '$match': {
                        'system_code': {
                            '$regex': '^20'
                        },
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': dict({
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }}, **({} if not user_allowed_storages else {
                        "storage_id": {"$in": user_allowed_storages}}))
                }, {
                    '$group': {
                        '_id': '$_id',
                        'item': {
                            '$addToSet': '$root_obj'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'item': {
                            '$first': '$item'
                        }
                    }
                }, {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$item.system_code', 0, 16
                            ]
                        },
                        'items': {
                            '$addToSet': '$item'
                        }
                    }
                }, {
                    '$project': {
                        'item': {
                            '$first': '$items'
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$item.brand',
                        'count': {
                            '$sum': 1
                        }
                    }
                }, {
                    '$project': {
                        'brand': '$_id',
                        '_id': 0,
                        'count': 1
                    }
                }
            ])
            brands_list = list()
            for brand in brands:
                kowsar_result = mongo.kowsar_collection.find_one(
                    {"brand": brand.get("brand"), "$expr": {"$eq": [{"$strLenCP": '$system_code'}, 9]}})
                brands_list.append({"name": brand.get("brand"), "label": kowsar_result.get("brand_label"),
                                    "image": kowsar_result.get("image"),
                                    "route": brand.get("brand").replace(" ", ""),
                                    "count": brand.get("count"),
                                    "system_code": kowsar_result.get("system_code"),
                                    })

            brands_list = sorted(brands_list, key=lambda x: x['system_code'], reverse=False)
            data = result.next().get("data") if result.alive else []
            for i in data:
                kowsar_result = mongo.kowsar_collection.find_one(
                    {"system_code": i.get("products")[0].get("system_code", '')})
                if kowsar_result.get("sub_category") == "Mobile":
                    label = kowsar_result.get("sub_category_label", "") + " " + kowsar_result.get("brand_label", "")
                else:
                    label = kowsar_result.get("sub_category_label")
                i['label'] = label
                product_list = list()
                for res in i.get("products", []):
                    if None in res['images']:
                        res['images'].remove(None)
                    res['image'] = res['images'][0] if res['images'] else None
                    res['name'] = res['name'].split(" | ")[0]
                    del res['images']
                    colors_list = list()
                    with RedisConnection() as redis:
                        for color in res.get('color', []):
                            colors_list.append(redis.client.hget(color, "hex"))
                    res['color'] = colors_list
                    prices_list = list()
                    if user_allowed_storages:
                        for sys_code in res['prices']:
                            for price in sys_code['prices']:
                                if price['storage_id'] in user_allowed_storages:
                                    prices_list.append(price)
                    else:
                        for sys_code in res['prices']:
                            for price in sys_code['prices']:
                                prices_list.append(price)

                    prices_list.sort(key=lambda x: x["regular"])
                    price, special_price = prices_list[0]["regular"], prices_list[0].get("special")
                    res['price'] = price
                    res['special_price'] = special_price
                    del res['prices']

                    product_list.append(res)

                i['products'] = product_list

            return {"mobile_brands": brands_list, "categories": data}

    @staticmethod
    def set_main_menu_banners(sliders, others):
        with MongoConnection() as mongo:
            result = mongo.banners.update_one({"name": "main_menu"}, {"$set": {"sliders": sliders, "others": others}},
                                              upsert=True)
            if result.modified_count or result.upserted_id:
                return True
            return False

    @staticmethod
    def get_main_manu_banners():
        with MongoConnection() as mongo:
            result = mongo.banners.find_one({"name": "main_menu"}, {"_id": 0, "name": 0})
            return result

    @staticmethod
    def get_products_seller(seller_id, page, per_page, from_date, to_date, from_qty, to_qty, from_price, to_price,
                            search):
        date_query = {}
        if from_date or to_date:
            date_query['date'] = {}
            if to_date:
                date_query['date']['$lte'] = to_date
            if from_date:
                date_query['date']['$gte'] = from_date

        match_queries = {}
        if from_qty or to_qty:
            match_queries['zz.v.inventory'] = {}
            if to_qty:
                match_queries['zz.v.inventory']['$lte'] = to_qty
            if from_qty:
                match_queries['zz.v.inventory']['$gte'] = from_qty
        if from_price or to_price:
            match_queries['zz.v.regular'] = {}
            if to_price:
                match_queries['zz.v.regular']['$lte'] = to_price
            if from_price:
                match_queries['zz.v.regular']['$gte'] = from_price
        if search:
            match_queries['root_obj.name'] = {'$regex': re.compile(rf"{search}(?i)")}

        with MongoConnection() as mongo:
            result = list(mongo.product.aggregate([
                {
                    '$match': dict({
                        'system_code': {
                            '$regex': f'.{{16}}{seller_id}.{{6}}$'
                        }
                    }, **date_query)
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$match': dict({
                        'zz.v.inventory': {
                            '$gt': 0
                        }
                    }, **match_queries)
                }, {
                    '$project': {
                        "_id": 0,
                        'system_code': 1,
                        'customer_type': 1,
                        'name': '$root_obj.name',
                        'color': '$root_obj.color',
                        'guaranty': '$root_obj.guaranty',
                        'inventory': '$zz.v.inventory',
                        'quantity': '$zz.v.quantity',
                        'storage_id': '$zz.v.storage_id',
                        'regular': '$zz.v.regular',
                        'reserved': '$zz.v.reserved',
                        'min_qty': '$zz.v.min_qty',
                        'max_qty': '$zz.v.max_qty',
                        'warehouse_label': '$zz.v.warehouse_label',
                        'special': '$zz.v.special',
                        'informal_price': '$zz.v.informal_price',
                        'special_from_date': '$zz.v.special_from_date',
                        'special_to_date': '$zz.v.special_to_date',
                        'date': '$root_obj.date'
                    }
                },
                {
                    "$facet": {
                        "data": [{"$skip": (page - 1) * per_page}, {"$limit": per_page}],
                        "count": [{"$count": "count"}]
                    }
                }
            ]))[0]
            if result:
                count = result.get("count", [{}])[0].get("count", 0) if result.get("count", [{}]) else 0
                return {"data": result.get("data"), "count": count}
            return None

    @staticmethod
    def system_code_exists(system_code):
        with MongoConnection() as mongo:
            result = mongo.product.find_one({"system_code": system_code})
            return True if result else False

    @staticmethod
    def add_credit_by_category(system_code, customer_type, credit):
        with MongoConnection() as mongo:
            warehouses_list = list(mongo.warehouses.find(
                {"isActive": True},
                {
                    "_id": 0,
                    "storage_id": {
                        "$convert": {"input": "$warehouse_id",
                                     "to": "string"}},
                }))
            query = {f"warehouse_details.{customer_type}.storages.{storage['storage_id']}.credit": credit for storage in
                     warehouses_list}
            result = mongo.product.update_many(
                {"system_code": {"$regex": f"^{system_code}"}},
                {"$set": query}
            )
            if result.modified_count:
                return True
            return False

    @staticmethod
    def mega_menu(customer_type, user_allowed_storages):
        with MongoConnection() as mongo:
            result = mongo.product.aggregate([
                {
                    '$match': {
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'min_qty': "$zz.v.min_qty",
                        'max_qty': {
                            '$cond': [
                                {
                                    '$gt': [
                                        {
                                            '$subtract': [
                                                '$zz.v.quantity', '$zz.v.reserved'
                                            ]
                                        }, '$zz.v.max_qty'
                                    ]
                                }, '$zz.v.max_qty', {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }
                            ]
                        },
                        'regular': '$zz.v.regular',
                        'special': {
                            '$cond': [
                                {
                                    '$and': [
                                        {
                                            '$gt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_from_date'
                                            ]
                                        }, {
                                            '$lt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_to_date'
                                            ]
                                        }
                                    ]
                                }, '$zz.v.special', None
                            ]
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': dict({
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }
                    }, **({} if not user_allowed_storages else {
                        "storage_id": {"$in": user_allowed_storages}}))
                }, {
                    '$group': {
                        '_id': {
                            'main': '$root_obj.main_category',
                            'sub': '$root_obj.sub_category',
                            'brand': '$root_obj.brand',
                            'syscode': {
                                '$substr': [
                                    '$system_code', 0, 9
                                ]
                            }
                        },
                        'fieldN': {
                            '$addToSet': '$root_obj'
                        }
                    }
                }, {
                    '$replaceRoot': {
                        'newRoot': '$_id'
                    }
                }, {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$syscode', 0, 6
                            ]
                        },
                        'fieldN': {
                            '$push': {
                                'name': '$brand',
                                'system_code': '$syscode'
                            }
                        },
                        'sub_category': {
                            '$first': '$sub'
                        },
                        'main': {
                            '$first': '$main'
                        }
                    }
                }, {
                    '$sort': {
                        '_id': 1
                    }
                },
                {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$_id', 0, 2
                            ]
                        },
                        'subs': {
                            '$push': {
                                'name': '$sub_category',
                                'system_code': '$_id',
                                'brands': '$fieldN'
                            }
                        },
                        'name': {
                            '$first': '$main'
                        }
                    }
                }, {
                    '$project': {
                        'system_code': '$_id',
                        'subs': 1,
                        'name': 1,
                        '_id': 0
                    }
                }
            ])
            mega_menu_data = list()
            for category in result:
                kowsar_data = mongo.kowsar_collection.find_one({"system_code": category.get("system_code")})
                category['label'] = kowsar_data.get("main_category_label")
                for sub in category.get("subs", []):
                    kowsar_data = mongo.kowsar_collection.find_one({"system_code": sub.get("system_code")})
                    sub['label'] = kowsar_data.get("sub_category_label")
                    for brand in sub.get("brands", []):
                        kowsar_data = mongo.kowsar_collection.find_one({"system_code": brand.get("system_code")})
                        brand['label'] = kowsar_data.get("brand_label")
                if category.get("name") == "Device":
                    mega_menu_data.extend(category.get("subs"))
                else:
                    mega_menu_data.append(category)
            return mega_menu_data

    @staticmethod
    def get_data_price_list_pic(system_code, customer_type, page, per_page, storage_id):
        skip = (page - 1) * per_page
        with MongoConnection() as mongo:
            result = mongo.product.aggregate([
                {
                    '$match': {
                        f'visible_in_site.{customer_type}': True,
                        'system_code': {
                            '$regex': f'^{system_code}'
                        }
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'min_qty': "$zz.v.min_qty",
                        'max_qty': {
                            '$cond': [
                                {
                                    '$gt': [
                                        {
                                            '$subtract': [
                                                '$zz.v.quantity', '$zz.v.reserved'
                                            ]
                                        }, '$zz.v.max_qty'
                                    ]
                                }, '$zz.v.max_qty', {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }
                            ]
                        },
                        'regular': '$zz.v.regular',
                        'special': {
                            '$cond': [
                                {
                                    '$and': [
                                        {
                                            '$gt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_from_date'
                                            ]
                                        }, {
                                            '$lt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_to_date'
                                            ]
                                        }
                                    ]
                                }, '$zz.v.special', None
                            ]
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': dict({
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }
                    }, **{} if not storage_id else {"storage_id": storage_id})
                },
                {
                    '$addFields': {
                        'name': {
                            '$substr': [
                                '$root_obj.name',
                                {
                                    "$add": [
                                        {
                                            '$strLenCP': '$root_obj.sub_category'
                                        },
                                        {
                                            '$strLenCP': '$root_obj.brand'
                                        },
                                        2
                                    ]
                                },
                                {
                                    '$strLenCP': '$root_obj.name'
                                }]
                        }
                    }
                }, {
                    '$group': {
                        '_id': {"name": "$name", "color": "$root_obj.color"},
                        'root_obj': {
                            '$first': '$root_obj'
                        },
                        'data': {
                            '$addToSet': {
                                '$concat': [
                                    {
                                        '$convert': {
                                            'to': 'string',
                                            'input': {
                                                '$divide': [
                                                    '$regular', 1000
                                                ]
                                            }
                                        }
                                    }, '/', '$root_obj.color'
                                ]
                            }
                        }
                    }
                }, {
                    "$group": {
                        "_id": "$_id.name",
                        'root_obj': {
                            '$first': '$root_obj'
                        },
                        'data': {
                            '$first': '$data'
                        },
                    }
                },
                {
                    "$sort": {
                        "root_obj.system_code": 1
                    }
                },
                {
                    "$skip": skip
                },
                {
                    "$limit": per_page
                },
                {
                    '$group': {
                        '_id': '$root_obj.brand',
                        'system_code': {
                            '$first': {
                                '$substr': [
                                    '$root_obj.system_code', 0, 9
                                ]
                            }
                        },
                        'data': {
                            '$push': {
                                'name': '$_id',
                                'prices': '$data'
                            }
                        }
                    }
                }, {
                    '$sort': {
                        'system_code': 1
                    }
                }, {
                    "$project": {
                        "brand": "$_id",
                        "system_code": 1,
                        "_id": 0,
                        "data": 1
                    }
                }
            ])
            result = list(result)
            rows = list()
            for brand in result:
                rows.append({
                    "name": "logo",
                    "image": f"https://api.aasood.com/gallery_files/iconpl/{brand['brand']}/117x36.jpg",
                })
                for i in brand.get("data", []):
                    prices = list()
                    for j in i.get("prices", []):
                        with RedisConnection() as redis:
                            hex_code = redis.client.hget(j.split("/")[1], "hex")
                            if hex_code:
                                j += "/" + hex_code
                            prices.append(j)
                    i.update({
                        "brand": brand.get("brand")
                    })
                    i['prices'] = prices
                rows.extend(brand.get("data", []))
            return rows

    @staticmethod
    def search_product_in_bot(name):
        pipe_lines = [{
            '$match': {
                'visible_in_site.B2B': True,
                'name': {
                    '$regex': re.compile(rf"{name}(?i)")
                },
            }
        }, {
            '$project': {
                'system_code': 1,
                'keys': {
                    '$objectToArray': '$warehouse_details'
                },
                'root_obj': '$$ROOT'
            }
        }, {
            '$unwind': '$keys'
        }, {
            '$project': {
                'system_code': 1,
                'customer_type': '$keys.k',
                'zz': {
                    '$objectToArray': '$keys.v.storages'
                },
                'root_obj': 1
            }
        }, {
            '$unwind': '$zz'
        }, {
            '$project': {
                'system_code': 1,
                'storage_id': '$zz.k',
                'customer_type': 1,
                'qty': {
                    '$subtract': [
                        '$zz.v.quantity', '$zz.v.reserved'
                    ]
                },
                'min': {
                    '$subtract': [
                        {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        }, '$zz.v.min_qty'
                    ]
                },
                'min_qty': "$zz.v.min_qty",
                'max_qty': {
                    '$cond': [
                        {
                            '$gt': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.max_qty'
                            ]
                        }, '$zz.v.max_qty', {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        }
                    ]
                },
                'regular': '$zz.v.regular',
                'special': {
                    '$cond': [
                        {
                            '$and': [
                                {
                                    '$gt': [
                                        jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        '$zz.v.special_from_date'
                                    ]
                                }, {
                                    '$lt': [
                                        jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        '$zz.v.special_to_date'
                                    ]
                                }
                            ]
                        }, '$zz.v.special', None
                    ]
                },
                'root_obj': 1
            }
        }, {
            '$match': {
                'customer_type': "B2B",
                'qty': {
                    '$gt': 0
                },
                'min': {
                    '$gte': 0
                }
            }
        }, {
            '$group': {
                '_id': {
                    "system_code": {
                        '$substr': [
                            '$system_code', 0, 16
                        ]}
                },
                'header': {
                    '$push': {
                        '$concat': [
                            '$root_obj.sub_category', '-', '$root_obj.brand'
                        ]
                    }
                },
                'name': {
                    '$push': '$root_obj.name'
                },
                'products': {
                    '$addToSet': {
                        'customer_type': '$customer_type',
                        'color': '$root_obj.color',
                        'guaranty': '$root_obj.guaranty',
                        'regular': '$regular',
                        'special': '$special',
                        'system_code': '$system_code',
                        "min_qty": "$min_qty",
                        "max_qty": "$max_qty"
                    }
                }
            }
        }, {
            '$project': {
                'system_code': '$_id.system_code',
                '_id': 0,
                'header': {
                    '$first': '$header'
                },
                'name': {
                    '$first': '$name'
                },
                'products': 1
            }
        }, {
            '$sort': {
                'name': 1
            }
        },
            {
                "$limit": 10
            },
            {
                '$group': {
                    '_id': '$header',
                    'system_code': {
                        '$push': '$system_code'
                    },
                    'models': {
                        '$push': {
                            'system_code': '$system_code',
                            'name': '$name',
                            'products': '$products'
                        }
                    }
                }
            }, {
                '$project': {
                    'name': '$_id',
                    'system_code': {
                        '$substr': [
                            {
                                '$first': '$system_code'
                            }, 0, 9
                        ]
                    },
                    '_id': 0,
                    'models': 1
                }
            }, {
                '$sort': {
                    'system_code': 1
                }
            }]
        with MongoConnection() as mongo:
            result = list(mongo.product.aggregate(pipe_lines))

            with RedisConnection() as redis:
                for group in result:
                    kowsar_data = mongo.kowsar_collection.find_one({"system_code": group["system_code"][:9]},
                                                                   {"_id": 0})
                    group['label'] = kowsar_data.get('sub_category_label',
                                                     kowsar_data.get("sub_category")) + ' ' + kowsar_data.get(
                        'brand_label', kowsar_data.get("brand"))
                    for model in group['models']:
                        for product in model['products']:
                            product['guaranty'] = {"value": product['guaranty'],
                                                   "label": redis.client.hget(product['guaranty'], "fa_ir")}
                            product['color'] = {"value": product['color'],
                                                "label": redis.client.hget(product['color'], "fa_ir")}

            return result

    @staticmethod
    def price_list_bot(customer_type, system_code, initial):
        with MongoConnection() as mongo:
            pipe_lines = [{
                '$match': {
                    f'visible_in_site.{customer_type}': True
                }
            }, {
                '$project': {
                    'system_code': 1,
                    'keys': {
                        '$objectToArray': '$warehouse_details'
                    },
                    'root_obj': '$$ROOT'
                }
            }, {
                '$unwind': '$keys'
            }, {
                '$project': {
                    'system_code': 1,
                    'customer_type': '$keys.k',
                    'zz': {
                        '$objectToArray': '$keys.v.storages'
                    },
                    'root_obj': 1
                }
            }, {
                '$unwind': '$zz'
            }, {
                '$project': {
                    'system_code': 1,
                    'storage_id': '$zz.k',
                    'customer_type': 1,
                    'qty': {
                        '$subtract': [
                            '$zz.v.quantity', '$zz.v.reserved'
                        ]
                    },
                    'min': {
                        '$subtract': [
                            {
                                '$subtract': [
                                    '$zz.v.quantity', '$zz.v.reserved'
                                ]
                            }, '$zz.v.min_qty'
                        ]
                    },
                    'min_qty': "$zz.v.min_qty",
                    'max_qty': {
                        '$cond': [
                            {
                                '$gt': [
                                    {
                                        '$subtract': [
                                            '$zz.v.quantity', '$zz.v.reserved'
                                        ]
                                    }, '$zz.v.max_qty'
                                ]
                            }, '$zz.v.max_qty', {
                                '$subtract': [
                                    '$zz.v.quantity', '$zz.v.reserved'
                                ]
                            }
                        ]
                    },
                    'regular': '$zz.v.regular',
                    'special': {
                        '$cond': [
                            {
                                '$and': [
                                    {
                                        '$gt': [
                                            jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            '$zz.v.special_from_date'
                                        ]
                                    }, {
                                        '$lt': [
                                            jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            '$zz.v.special_to_date'
                                        ]
                                    }
                                ]
                            }, '$zz.v.special', None
                        ]
                    },
                    'root_obj': 1
                }
            }, {
                '$match': {
                    'customer_type': customer_type,
                    'qty': {
                        '$gt': 0
                    },
                    'min': {
                        '$gte': 0
                    }
                }
            }]
            if initial:
                pipe_lines.extend([{
                    '$replaceRoot': {
                        'newRoot': '$root_obj'
                    }
                }, {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$system_code', 0, 6
                            ]
                        },
                        'fieldN': {
                            '$addToSet': '$sub_category'
                        }
                    }
                }, {
                    '$project': {
                        'system_code': '$_id',
                        '_id': 0,
                        'name': {
                            '$first': '$fieldN'
                        }
                    }
                }, {
                    '$sort': {
                        'system_code': 1
                    }
                }])
            else:
                pipe_lines.extend([{"$match": {"system_code": {"$regex": "^" + system_code}}},
                                   {
                                       '$group': {
                                           '_id': {
                                               "system_code": {
                                                   '$substr': [
                                                       '$system_code', 0, 16
                                                   ]},
                                               'storage_id': '$storage_id'
                                           },
                                           'header': {
                                               '$push': {
                                                   '$concat': [
                                                       '$root_obj.sub_category', '-', '$root_obj.brand'
                                                   ]
                                               }
                                           },
                                           'name': {
                                               '$push': '$root_obj.name'
                                           },
                                           'products': {
                                               '$push': {
                                                   'customer_type': '$customer_type',
                                                   'color': '$root_obj.color',
                                                   'guaranty': '$root_obj.guaranty',
                                                   'regular': '$regular',
                                                   'special': '$special',
                                                   'system_code': '$system_code',
                                                   "min_qty": "$min_qty",
                                                   "max_qty": "$max_qty"
                                               }
                                           }
                                       }
                                   }, {
                                       '$project': {
                                           'system_code': '$_id.system_code',
                                           '_id': 0,
                                           'header': {
                                               '$first': '$header'
                                           },
                                           'name': {
                                               '$first': '$name'
                                           },
                                           'products': 1
                                       }
                                   }, {
                                       '$sort': {
                                           'name': 1
                                       }
                                   }, {
                                       '$group': {
                                           '_id': '$header',
                                           'system_code': {
                                               '$push': '$system_code'
                                           },
                                           'models': {
                                               '$push': {
                                                   'system_code': '$system_code',
                                                   'name': '$name',
                                                   'products': '$products'
                                               }
                                           }
                                       }
                                   }, {
                                       '$project': {
                                           'name': '$_id',
                                           'system_code': {
                                               '$substr': [
                                                   {
                                                       '$first': '$system_code'
                                                   }, 0, 9
                                               ]
                                           },
                                           '_id': 0,
                                           'models': 1
                                       }
                                   }, {
                                       '$sort': {
                                           'system_code': 1
                                       }
                                   }])
            result = list(mongo.product.aggregate(pipe_lines))
            if initial:
                for category in result:
                    kowsar_data = mongo.kowsar_collection.find_one({"system_code": category.get('system_code')})
                    kowsar_data = kowsar_data if kowsar_data else {}
                    category['label'] = kowsar_data.get('sub_category_label') if kowsar_data.get(
                        "sub_category_label") else category.get('sub_category')
            else:
                with RedisConnection() as redis:
                    for group in result:
                        kowsar_data = mongo.kowsar_collection.find_one({"system_code": group["system_code"][:9]},
                                                                       {"_id": 0})
                        group['label'] = kowsar_data.get('sub_category_label',
                                                         kowsar_data.get("sub_category")) + ' ' + kowsar_data.get(
                            'brand_label', kowsar_data.get("brand"))
                        for model in group['models']:
                            for product in model['products']:
                                product['guaranty'] = {"value": product['guaranty'],
                                                       "label": redis.client.hget(product['guaranty'], "fa_ir")}
                                product['color'] = {"value": product['color'],
                                                    "label": redis.client.hget(product['color'], "fa_ir")}
            return result

    @staticmethod
    def get_basket_products(system_codes, storage_id, customer_type):
        with MongoConnection() as mongo:
            warehouse_query_string = f"$warehouse_details.{customer_type}.storages.{storage_id}"
            pipe_lines = [
                {
                    '$match': {
                        'system_code': {"$in": system_codes}
                    }
                }, {
                    '$addFields': {
                        'regular': f'{warehouse_query_string}.regular',
                        'special': {
                            '$cond': [
                                {
                                    '$and': [
                                        {
                                            '$gt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                f'{warehouse_query_string}.special_from_date'
                                            ]
                                        }, {
                                            '$lt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                f'{warehouse_query_string}.special_to_date'
                                            ]
                                        }
                                    ]
                                }, f'{warehouse_query_string}.special', None
                            ]
                        },
                        "quantity": {"$subtract": [f"{warehouse_query_string}.quantity",
                                                   f"{warehouse_query_string}.reserved"]},
                        "min_qty": f"{warehouse_query_string}.min_qty",
                        "max_qty": f"{warehouse_query_string}.max_qty"
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'warehouse_details': 0
                    }
                }
            ]
            result = list(mongo.product.aggregate(pipe_lines))
            lang = "fa_ir"
            with RedisConnection() as redis:
                for product in result:
                    product['color'] = {"value": product['color'], "label": redis.client.hget(product['color'], lang)}
                    product['guaranty'] = {"value": product['guaranty'],
                                           "label": redis.client.hget(product['guaranty'], lang)}
                    product['seller'] = {"value": product['seller'],
                                         "label": redis.client.hget(product['seller'], lang)}

                    kowsar_data = mongo.kowsar_collection.find_one({"system_code": product.get("system_code")[:9]},
                                                                   {"_id": 0})
                    product['sub_category'] = {"value": product['sub_category'],
                                               "label": kowsar_data.get('sub_category_label') if kowsar_data else None}
                    product['main_category'] = {"value": product['main_category'],
                                                "label": kowsar_data.get(
                                                    'main_category_label') if kowsar_data else None}
                    product['brand'] = {"value": product['brand'],
                                        "label": kowsar_data.get('brand_label') if kowsar_data else None}
            if result:
                return result
            return None

    @staticmethod
    def get_items(system_code, customer_type, storage_id):
        with MongoConnection() as mongo:
            pipe_line = [{
                '$match': {
                    f'visible_in_site.{customer_type}': True
                }
            }, {
                '$project': {
                    'system_code': 1,
                    'keys': {
                        '$objectToArray': '$warehouse_details'
                    },
                    'root_obj': '$$ROOT'
                }
            }, {
                '$unwind': '$keys'
            }, {
                '$project': {
                    'system_code': 1,
                    'customer_type': '$keys.k',
                    'zz': {
                        '$objectToArray': '$keys.v.storages'
                    },
                    'root_obj': 1
                }
            }, {
                '$unwind': '$zz'
            }, {
                '$project': {
                    'system_code': 1,
                    'storage_id': '$zz.k',
                    "storage_label": "$zz.v.warehouse_label",
                    'customer_type': 1,
                    'qty': {
                        '$subtract': [
                            '$zz.v.quantity', '$zz.v.reserved'
                        ]
                    },
                    'min': {
                        '$subtract': [
                            {
                                '$subtract': [
                                    '$zz.v.quantity', '$zz.v.reserved'
                                ]
                            }, '$zz.v.min_qty'
                        ]
                    },
                    'min_qty': '$zz.v.min_qty',
                    'max_qty': {
                        '$cond': [
                            {
                                '$gt': [
                                    {
                                        '$subtract': [
                                            '$zz.v.quantity', '$zz.v.reserved'
                                        ]
                                    }, '$zz.v.max_qty'
                                ]
                            }, '$zz.v.max_qty', {
                                '$subtract': [
                                    '$zz.v.quantity', '$zz.v.reserved'
                                ]
                            }
                        ]
                    },
                    'regular': '$zz.v.regular',
                    'special': {
                        '$cond': [
                            {
                                '$and': [
                                    {
                                        '$gt': [
                                            jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            '$zz.v.special_from_date'
                                        ]
                                    }, {
                                        '$lt': [
                                            jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            '$zz.v.special_to_date'
                                        ]
                                    }
                                ]
                            }, '$zz.v.special', None
                        ]
                    },
                    'root_obj': 1
                }
            }, {
                '$match': dict({
                    'customer_type': customer_type,
                    'qty': {
                        '$gt': 0
                    },
                    'min': {
                        '$gte': 0
                    }
                }, **({} if not storage_id else {"storage_id": storage_id}))
            }]
            if len(system_code) != 25:
                if system_code == '00':
                    index = 2
                    name = '$root_obj.main_category'
                elif len(system_code) == 2:
                    pipe_line[0]['$match']['system_code'] = {"$regex": "^" + system_code}
                    index = 6
                    name = '$root_obj.sub_category'
                elif len(system_code) == 6:
                    pipe_line[0]['$match']['system_code'] = {"$regex": "^" + system_code}
                    index = 9
                    name = '$root_obj.brand'
                elif len(system_code) == 9:
                    pipe_line[0]['$match']['system_code'] = {"$regex": "^" + system_code}
                    index = 13
                    name = '$root_obj.model'
                elif len(system_code) == 13:
                    pipe_line[0]['$match']['system_code'] = {"$regex": "^" + system_code}
                    index = 16
                    name = {'$reduce': {
                        'input': {"$objectToArray": "$root_obj.configs"},
                        'initialValue': '',
                        'in': {
                            '$concat': [
                                '$$value',
                                {'$cond': [{'$eq': ['$$value', '']}, '', ' ']},
                                '$$this.v']
                        }
                    }}
                elif len(system_code) == 16:
                    pipe_line[0]['$match']['system_code'] = {"$regex": "^" + system_code}
                    index = 19
                    name = '$root_obj.seller'
                elif len(system_code) == 19:
                    pipe_line[0]['$match']['system_code'] = {"$regex": "^" + system_code}
                    index = 22
                    name = '$root_obj.color'
                elif len(system_code) == 22:
                    pipe_line[0]['$match']['system_code'] = {"$regex": "^" + system_code}
                    index = 25
                    name = '$root_obj.guaranty'

                pipe_line.extend([{
                    "$group": {
                        "_id": None,
                        "fieldN": {
                            "$addToSet": {
                                "system_code": {"$substr": ["$root_obj.system_code", 0, index]},
                                "name": name
                            },
                        }
                    }
                }, {
                    '$unwind': '$fieldN'
                }, {
                    '$replaceRoot': {
                        'newRoot': '$fieldN'
                    }
                }, {
                    '$sort': {
                        'system_code': 1
                    }
                }])
            else:
                pipe_line[0]['$match']['system_code'] = system_code
                pipe_line.append({
                    "$project": {
                        '_id': 0,
                        'system_code': "$system_code",
                        'brand': "$root_obj.brand",
                        'color': "$root_obj.color",
                        'guaranty': "$root_obj.guaranty",
                        'main_category': "$root_obj.main_category",
                        'seller': "$root_obj.seller",
                        'sub_category': "$root_obj.sub_category",
                        'storage_label': "$storage_label",
                        'storage_id': "$storage_id",
                        'price': "$regular",
                        'special_price': "$special",
                        'max_qty': "$max_qty",
                        'min_qty': "$min_qty",
                        "name": "$root_obj.name",
                        "quantity": "$qty"
                    }
                })
            result = mongo.product.aggregate(pipe_line)
            return list(result)

    @staticmethod
    def price_list_all(customer_type, sub_category, brand, model, allowed_storages):
        with MongoConnection() as mongo:
            pipe_lines = [
                {
                    '$match': {
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        "storage_label": "$zz.v.warehouse_label",
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'min_qty': '$zz.v.min_qty',
                        'max_qty': {
                            '$cond': [
                                {
                                    '$gt': [
                                        {
                                            '$subtract': [
                                                '$zz.v.quantity', '$zz.v.reserved'
                                            ]
                                        }, '$zz.v.max_qty'
                                    ]
                                }, '$zz.v.max_qty', {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }
                            ]
                        },
                        'regular': '$zz.v.regular',
                        'special': {
                            '$cond': [
                                {
                                    '$and': [
                                        {
                                            '$gt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_from_date'
                                            ]
                                        }, {
                                            '$lt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_to_date'
                                            ]
                                        }
                                    ]
                                }, '$zz.v.special', None
                            ]
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': dict({
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }
                    }, **({} if not allowed_storages else {'storage_id': {
                        '$in': allowed_storages
                    }}))
                }, {
                    '$group': {
                        '_id': {
                            'system_code': {
                                '$substr': [
                                    '$system_code', 0, 16
                                ]
                            },
                            'storage_id': '$storage_id',
                            'storage_label': '$storage_label'
                        },
                        'header': {
                            '$push': {
                                '$concat': [
                                    '$root_obj.sub_category', '-', '$root_obj.brand'
                                ]
                            }
                        },
                        'name': {
                            '$push': '$root_obj.name'
                        },
                        'products': {
                            '$push': {
                                'storage_id': '$storage_id',
                                'customer_type': '$customer_type',
                                'color': '$root_obj.color',
                                'guaranty': '$root_obj.guaranty',
                                'regular': '$regular',
                                'special': '$special',
                                'system_code': '$system_code',
                                'min_qty': '$min_qty',
                                'max_qty': '$max_qty'
                            }
                        }
                    }
                }, {
                    '$project': {
                        'system_code': '$_id.system_code',
                        'storage_id': '$_id.storage_id',
                        'storage_label': '$_id.storage_label',
                        '_id': 0,
                        'header': {
                            '$first': '$header'
                        },
                        'name': {
                            '$first': '$name'
                        },
                        'products': 1
                    }
                }, {
                    '$sort': {
                        'name': 1
                    }
                }, {
                    '$group': {
                        '_id': {
                            'header': '$header',
                            'storage_id': '$storage_id',
                            'storage_label': '$storage_label'
                        },
                        'system_code': {
                            '$push': '$system_code'
                        },
                        'models': {
                            '$push': {
                                'system_code': '$system_code',
                                'name': '$name',
                                'products': '$products'
                            }
                        }
                    }
                }, {
                    '$project': {
                        'name': '$_id.header',
                        'storage_id': '$_id.storage_id',
                        'storage_label': '$_id.storage_label',
                        'system_code': {
                            '$substr': [
                                {
                                    '$first': '$system_code'
                                }, 0, 9
                            ]
                        },
                        '_id': 0,
                        'models': 1
                    }
                }, {
                    '$sort': {
                        'system_code': 1
                    }
                }, {
                    '$group': {
                        '_id': {
                            'storage_id': '$storage_id',
                            'storage_label': '$storage_label'
                        },
                        'data': {
                            '$push': {
                                'system_code': '$system_code',
                                'name': '$name',
                                'models': '$models'
                            }
                        }
                    }
                }, {
                    '$project': {
                        'storage_id': '$_id.storage_id',
                        'storage_label': '$_id.storage_label',
                        '_id': 0,
                        'data': 1
                    }
                }
            ]
            if sub_category:
                pipe_lines[7]['$match']["root_obj.sub_category"] = sub_category
            if brand:
                pipe_lines[7]['$match']["root_obj.brand"] = brand
            if model:
                pipe_lines[7]['$match']["root_obj.model"] = model
            db_data = list(mongo.product.aggregate(pipe_lines))
            return db_data

    @staticmethod
    def get_basket_product(system_code, storage_id, customer_type):
        with MongoConnection() as mongo:
            warehouse_query_string = f"$warehouse_details.{customer_type}.storages.{storage_id}"
            pipe_lines = [
                {
                    '$match': {
                        'system_code': system_code
                    }
                }, {
                    '$addFields': {
                        'regular': f'{warehouse_query_string}.regular',
                        'special': {
                            '$cond': [
                                {
                                    '$and': [
                                        {
                                            '$gt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                f'{warehouse_query_string}.special_from_date'
                                            ]
                                        }, {
                                            '$lt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                f'{warehouse_query_string}.special_to_date'
                                            ]
                                        }
                                    ]
                                }, f'{warehouse_query_string}.special', None
                            ]
                        },
                        "quantity": {"$subtract": [f"{warehouse_query_string}.quantity",
                                                   f"{warehouse_query_string}.reserved"]},
                        "min_qty": f"{warehouse_query_string}.min_qty",
                        "max_qty": f"{warehouse_query_string}.max_qty"
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'warehouse_details': 0
                    }
                }, {
                    "$limit": 1
                }
            ]
            result = list(mongo.product.aggregate(pipe_lines))
            if result:
                return result[0]
            return None

    @staticmethod
    def price_list_tehran(customer_type, sub_category, brand, model, allowed_storages):
        with MongoConnection() as mongo:
            pipe_lines = [
                {
                    '$match': {
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        "storage_label": "$zz.v.warehouse_label",
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'min_qty': '$zz.v.min_qty',
                        'max_qty': {
                            '$cond': [
                                {
                                    '$gt': [
                                        {
                                            '$subtract': [
                                                '$zz.v.quantity', '$zz.v.reserved'
                                            ]
                                        }, '$zz.v.max_qty'
                                    ]
                                }, '$zz.v.max_qty', {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }
                            ]
                        },
                        'regular': '$zz.v.regular',
                        'special': {
                            '$cond': [
                                {
                                    '$and': [
                                        {
                                            '$gt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_from_date'
                                            ]
                                        }, {
                                            '$lt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_to_date'
                                            ]
                                        }
                                    ]
                                }, '$zz.v.special', None
                            ]
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': {
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        },
                    }
                },
                {
                    "$facet": {
                        "filters": [
                            {
                                '$replaceRoot': {
                                    'newRoot': '$root_obj'
                                }
                            },
                            {
                                '$group': {
                                    '_id': None,
                                    'data': {
                                        '$addToSet': {
                                            'sub_category': '$sub_category',
                                            'brand': '$brand',
                                            'model': '$model',
                                            'system_code': '$system_code'
                                        }
                                    }
                                }
                            }, {
                                '$unwind': '$data'
                            }, {
                                '$group': {
                                    '_id': {
                                        'brand': '$data.brand',
                                        'sub': '$data.sub_category'
                                    },
                                    'system_code': {
                                        '$addToSet': {
                                            '$substr': [
                                                '$data.system_code', 0, 6
                                            ]
                                        }
                                    },
                                    'models': {
                                        '$addToSet': '$data.model'
                                    }
                                }
                            }, {
                                '$group': {
                                    '_id': '$_id.sub',
                                    'brands': {
                                        '$push': {
                                            'brand': '$_id.brand',
                                            'models': '$models',
                                            'system_code': {
                                                '$first': '$system_code'
                                            }
                                        }
                                    }
                                }
                            }, {
                                '$project': {
                                    'name': '$_id',
                                    'brands': 1,
                                    '_id': 0
                                }
                            }, {
                                '$sort': {
                                    'brands.system_code': 1
                                }
                            }
                        ],
                        "products": [
                            {
                                "$match": {}
                            },
                            {
                                '$group': {
                                    '_id': {
                                        'system_code': {
                                            '$substr': [
                                                '$system_code', 0, 16
                                            ]
                                        }
                                    },
                                    'header': {
                                        '$push': {
                                            '$concat': [
                                                '$root_obj.sub_category', '-', '$root_obj.brand'
                                            ]
                                        }
                                    },
                                    'name': {
                                        '$push': '$root_obj.name'
                                    },
                                    'products': {
                                        '$push': {
                                            'storage_id': '$storage_id',
                                            'customer_type': '$customer_type',
                                            'color': '$root_obj.color',
                                            'guaranty': '$root_obj.guaranty',
                                            'regular': '$regular',
                                            'special': '$special',
                                            'system_code': '$system_code',
                                            'min_qty': '$min_qty',
                                            'max_qty': '$max_qty'
                                        }
                                    }
                                }
                            }, {
                                '$project': {
                                    'system_code': '$_id.system_code',
                                    'storage_id': '$_id.storage_id',
                                    'storage_label': '$_id.storage_label',
                                    '_id': 0,
                                    'header': {
                                        '$first': '$header'
                                    },
                                    'name': {
                                        '$first': '$name'
                                    },
                                    'products': 1
                                }
                            }, {
                                '$sort': {
                                    'name': 1
                                }
                            }, {
                                '$group': {
                                    '_id': {
                                        'header': '$header',
                                        'storage_id': '$storage_id',
                                        'storage_label': '$storage_label'
                                    },
                                    'system_code': {
                                        '$push': '$system_code'
                                    },
                                    'models': {
                                        '$push': {
                                            'system_code': '$system_code',
                                            'name': '$name',
                                            'products': '$products'
                                        }
                                    }
                                }
                            }, {
                                '$project': {
                                    'name': '$_id.header',
                                    'storage_id': '$_id.storage_id',
                                    'storage_label': '$_id.storage_label',
                                    'system_code': {
                                        '$substr': [
                                            {
                                                '$first': '$system_code'
                                            }, 0, 9
                                        ]
                                    },
                                    '_id': 0,
                                    'models': 1
                                }
                            }, {
                                '$sort': {
                                    'system_code': 1
                                }
                            }
                        ]
                    }
                }
            ]
            if allowed_storages:
                pipe_lines[6]['$match']['storage_id'] = {'$in': allowed_storages}
            if sub_category:
                pipe_lines[7]["$facet"]['products'][0]['$match']["root_obj.sub_category"] = sub_category
            if brand:
                pipe_lines[7]["$facet"]['products'][0]['$match']["root_obj.brand"] = brand
            if model:
                pipe_lines[7]["$facet"]['products'][0]['$match']["root_obj.model"] = model
            db_data = list(mongo.product.aggregate(pipe_lines))
            db_data = db_data[0] if db_data else {}
            filters = db_data.get('filters')
            db_data = db_data.get("products")
            for _filter in filters:
                for brand in _filter.get("brands", []):
                    kowsar_data = mongo.kowsar_collection.find_one(
                        {"brand": brand.get("brand"), "sub_category": _filter.get("name"),
                         "system_code": {"$regex": ".{25}"}})
                    brand['label'] = kowsar_data.get('brand_label', brand.get('brand'))
                _filter['label'] = kowsar_data.get('sub_category_label', _filter.get("name"))

            with RedisConnection() as redis:
                for group in db_data:
                    kowsar_data = mongo.kowsar_collection.find_one({"system_code": group["system_code"][:9]},
                                                                   {"_id": 0})
                    group['name'] = kowsar_data.get('sub_category_label',
                                                    kowsar_data.get("sub_category")) + ' ' + kowsar_data.get(
                        'brand_label', kowsar_data.get("brand"))
                    for model in group['models']:
                        for product in model['products']:
                            product['guaranty'] = {"value": product['guaranty'],
                                                   "label": redis.client.hget(product['guaranty'], "fa_ir")}
                            product['color'] = {"value": product['color'],
                                                "label": redis.client.hget(product['color'], "fa_ir")}

            return {'data': db_data, "filters": filters}

    @staticmethod
    def price_list(customer_type, storage_id, sub_category, brand, model, allowed_storages):
        with MongoConnection() as mongo:
            pipe_lines = [
                {
                    '$match': {
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'min_qty': "$zz.v.min_qty",
                        'max_qty': {
                            '$cond': [
                                {
                                    '$gt': [
                                        {
                                            '$subtract': [
                                                '$zz.v.quantity', '$zz.v.reserved'
                                            ]
                                        }, '$zz.v.max_qty'
                                    ]
                                }, '$zz.v.max_qty', {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }
                            ]
                        },
                        'regular': '$zz.v.regular',
                        'special': {
                            '$cond': [
                                {
                                    '$and': [
                                        {
                                            '$gt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_from_date'
                                            ]
                                        }, {
                                            '$lt': [
                                                jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                '$zz.v.special_to_date'
                                            ]
                                        }
                                    ]
                                }, '$zz.v.special', None
                            ]
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': {
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        },
                        "storage_id": '1'
                    }
                },
                {
                    "$facet": {
                        "filters": [
                            {
                                '$replaceRoot': {
                                    'newRoot': '$root_obj'
                                }
                            },
                            {
                                '$group': {
                                    '_id': None,
                                    'data': {
                                        '$addToSet': {
                                            'sub_category': '$sub_category',
                                            'brand': '$brand',
                                            'model': '$model',
                                            'system_code': '$system_code'
                                        }
                                    }
                                }
                            }, {
                                '$unwind': '$data'
                            }, {
                                '$group': {
                                    '_id': {
                                        'brand': '$data.brand',
                                        'sub': '$data.sub_category'
                                    },
                                    'system_code': {
                                        '$addToSet': {
                                            '$substr': [
                                                '$data.system_code', 0, 6
                                            ]
                                        }
                                    },
                                    'models': {
                                        '$addToSet': '$data.model'
                                    }
                                }
                            }, {
                                '$group': {
                                    '_id': '$_id.sub',
                                    'brands': {
                                        '$push': {
                                            'brand': '$_id.brand',
                                            'models': '$models',
                                            'system_code': {
                                                '$first': '$system_code'
                                            }
                                        }
                                    }
                                }
                            }, {
                                '$project': {
                                    'name': '$_id',
                                    'brands': 1,
                                    '_id': 0
                                }
                            }, {
                                '$sort': {
                                    'brands.system_code': 1
                                }
                            }
                        ],
                        "products": [
                            {"$match": {}},
                            {
                                '$group': {
                                    '_id': {
                                        '$substr': [
                                            '$system_code', 0, 16
                                        ]
                                    },
                                    'header': {
                                        '$push': {
                                            '$concat': [
                                                '$root_obj.sub_category', '-', '$root_obj.brand'
                                            ]
                                        }
                                    },
                                    'name': {
                                        '$push': '$root_obj.name'
                                    },
                                    'products': {
                                        '$push': {
                                            'storage_id': '$storage_id',
                                            'customer_type': '$customer_type',
                                            'color': '$root_obj.color',
                                            'guaranty': '$root_obj.guaranty',
                                            'regular': '$regular',
                                            'special': '$special',
                                            'system_code': '$system_code',
                                            "min_qty": "$min_qty",
                                            "max_qty": "$max_qty"
                                        }
                                    }
                                }
                            }, {
                                '$project': {
                                    'system_code': '$_id',
                                    '_id': 0,
                                    'header': {
                                        '$first': '$header'
                                    },
                                    'name': {
                                        '$first': '$name'
                                    },
                                    'products': 1
                                }
                            }, {
                                '$sort': {
                                    'name': 1
                                }
                            }, {
                                '$group': {
                                    '_id': '$header',
                                    'system_code': {
                                        '$push': '$system_code'
                                    },
                                    'models': {
                                        '$push': {
                                            'system_code': '$system_code',
                                            'name': '$name',
                                            'products': '$products'
                                        }
                                    }
                                }
                            }, {
                                '$project': {
                                    'name': '$_id',
                                    'system_code': {
                                        '$substr': [
                                            {
                                                '$first': '$system_code'
                                            }, 0, 9
                                        ]
                                    },
                                    '_id': 0,
                                    'models': 1
                                }
                            }, {
                                '$sort': {
                                    'system_code': 1
                                }
                            }
                        ]
                    }
                }
            ]
            if storage_id or allowed_storages:
                pipe_lines[6]['$match']["storage_id"] = storage_id if storage_id else allowed_storages[0]
            if storage_id == '-1':
                del pipe_lines[6]['$match']["storage_id"]
                pipe_lines[7]['$facet']['products'][1]['$group']["_id"] = {
                    'a': {
                        '$substr': [
                            '$system_code', 0, 16
                        ]
                    },
                    'b': '$root_obj.color',
                    'c': '$root_obj.guaranty'
                }
                pipe_lines[7]['$facet']['products'].insert(2, {"$group": {
                    "_id": "$_id.a",
                    "products": {
                        "$push": {"$first": "$products"}
                    },
                    "header": {
                        "$first": "$header"
                    },
                    "name": {
                        "$first": "$name"
                    }
                }})
            if sub_category:
                pipe_lines[7]['$facet']['products'][0]['$match']["root_obj.sub_category"] = sub_category
            if brand:
                pipe_lines[7]['$facet']['products'][0]['$match']["root_obj.brand"] = brand
            if model:
                pipe_lines[7]['$facet']['products'][0]['$match']["root_obj.model"] = model

            db_data = list(mongo.product.aggregate(pipe_lines))
            db_data = db_data[0]
            filters = db_data.get('filters')
            db_data = db_data.get("products")

            for _filter in filters:
                for brand in _filter.get("brands", []):
                    kowsar_data = mongo.kowsar_collection.find_one(
                        {"brand": brand.get("brand"), "sub_category": _filter.get("name"),
                         "system_code": {"$regex": ".{25}"}})
                    brand['label'] = kowsar_data.get('brand_label', brand.get('brand'))
                _filter['label'] = kowsar_data.get('sub_category_label', _filter.get("name"))

            storages_query = {
                "isActive": True
            }
            if allowed_storages:
                storages_query.update({"warehouse_id": {"$in": list(map(int, allowed_storages))}})

            storages_labels = list(
                mongo.warehouses.find(
                    storages_query,
                    {"_id": 0, "storage_id": {"$convert": {"input": "$warehouse_id", "to": "string"}},
                     "label": "$warehouse_name",
                     "active": {"$cond": [{"$eq": ["$warehouse_id", int(storage_id) if storage_id else int(
                         allowed_storages[0]) if allowed_storages else 1]}, True, False]}}))
            storages_labels.append({
                "storage_id": "-1",
                "label": "???????? ?????????? ????",
                "active": True if storage_id == '-1' else False
            })

            with RedisConnection() as redis:
                for group in db_data:
                    kowsar_data = mongo.kowsar_collection.find_one({"system_code": group["system_code"][:9]},
                                                                   {"_id": 0})
                    group['name'] = kowsar_data.get('sub_category_label',
                                                    kowsar_data.get("sub_category")) + ' ' + kowsar_data.get(
                        'brand_label', kowsar_data.get("brand"))
                    for model in group['models']:
                        for product in model['products']:
                            product['guaranty'] = {"value": product['guaranty'],
                                                   "label": redis.client.hget(product['guaranty'], "fa_ir")}
                            product['color'] = {"value": product['color'],
                                                "label": redis.client.hget(product['color'], "fa_ir")}

        return {'data': db_data, "storages": storages_labels, "filters": filters}

    @staticmethod
    def search_product_child(name, system_code, storages, customer_type, in_stock):
        with MongoConnection() as mongo:
            pipe_lines = [
                {
                    '$match': {
                        'step': 4
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                    }
                },
                {
                    "$addFields": {
                        "GIN": None
                    }
                }
            ]
            if not system_code:
                pipe_lines[0]['$match']['name'] = {'$regex': re.compile(fr"{name}(?i)")}
            else:
                pipe_lines[0]['$match']['system_code'] = system_code

            if in_stock:
                temp = [
                    {
                        '$project': {
                            'system_code': 1,
                            'keys': {
                                '$objectToArray': '$warehouse_details'
                            },
                            'root_obj': '$$ROOT'
                        }
                    }, {
                        '$unwind': '$keys'
                    }, {
                        '$project': {
                            'system_code': 1,
                            'customer_type': '$keys.k',
                            'zz': {
                                '$objectToArray': '$keys.v.storages'
                            },
                            'root_obj': 1
                        }
                    }, {
                        '$unwind': '$zz'
                    }, {
                        '$project': {
                            'system_code': 1,
                            'storage_id': '$zz.k',
                            'customer_type': 1,
                            'qty': {
                                '$subtract': [
                                    '$zz.v.quantity', '$zz.v.reserved'
                                ]
                            },
                            'min': {
                                '$subtract': [
                                    {
                                        '$subtract': [
                                            '$zz.v.quantity', '$zz.v.reserved'
                                        ]
                                    }, '$zz.v.min_qty'
                                ]
                            },
                            'price': {
                                'storage_id': '$zz.k',
                                'regular': '$zz.v.regular',
                                'special': '$zz.v.special'
                            },
                            'root_obj': 1
                        }
                    }, {
                        '$match': {
                            'customer_type': customer_type,
                            'qty': {
                                '$gt': 0
                            },
                            'min': {
                                '$gte': 0
                            },
                            "storage_id": {"$in": storages}
                        }
                    }, {
                        '$replaceRoot': {
                            'newRoot': '$root_obj'
                        }
                    }
                ]
                temp.extend(pipe_lines)
                pipe_lines = temp

            result = mongo.product.aggregate(pipe_lines)
            return list(result)

    @staticmethod
    def get_product_by_name(name, storages, user_allowed_storages, customer_type):
        with MongoConnection() as mongo:
            warehouses_query = dict({"isActive": True}, **(
                {} if not user_allowed_storages else {"warehouse_id": {"$in": list(map(int, user_allowed_storages))}}))
            storages_labels = list(
                mongo.warehouses.find(warehouses_query,
                                      {"_id": 0, "storage_id": {"$convert": {"input": "$warehouse_id", "to": "string"}},
                                       "label": "$warehouse_name"}))

            pipe_lines = [
                {
                    '$match': {
                        'name': {
                            '$regex': re.compile(rf"{name}(?i)")
                        },
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'price': {
                            'storage_id': '$zz.k',
                            'regular': '$zz.v.regular',
                            'special': {
                                '$cond': [
                                    {
                                        '$and': [
                                            {
                                                '$gt': [
                                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                    '$zz.v.special_from_date'
                                                ]
                                            }, {
                                                '$lt': [
                                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                    '$zz.v.special_to_date'
                                                ]
                                            }
                                        ]
                                    }, '$zz.v.special', None
                                ]
                            }
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': {
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$_id',
                        'item': {
                            '$addToSet': '$root_obj'
                        },
                        'prices': {
                            '$addToSet': '$price'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'item': {
                            '$first': '$item'
                        },
                        'prices': 1
                    }
                }, {
                    '$project': {
                        'system_code': '$item.system_code',
                        'name': '$item.name',
                        'color': '$item.color',
                        'attributes': '$item.attributes',
                        'prices': 1
                    }
                }, {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$system_code', 0, 16
                            ]
                        },
                        'name': {
                            '$first': '$name'
                        },
                        'products': {
                            '$push': '$$ROOT'
                        },
                        'prices': {
                            '$push': {
                                'system_code': '$system_code',
                                'prices': '$prices'
                            }
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'products': 1,
                        'name': 1,
                        'system_code': '$_id',
                        'color': {
                            '$setIntersection': {
                                '$reduce': {
                                    'input': '$products',
                                    'initialValue': [],
                                    'in': {
                                        '$concatArrays': [
                                            '$$value', [
                                                '$$this.color'
                                            ]
                                        ]
                                    }
                                }
                            }
                        },
                        'images': {
                            '$setIntersection': {
                                '$reduce': {
                                    'input': '$products',
                                    'initialValue': [],
                                    'in': {
                                        '$concatArrays': [
                                            '$$value', [
                                                '$$this.attributes.mainImage-pd'
                                            ]
                                        ]
                                    }
                                }
                            }
                        },
                        'prices': 1
                    }
                }, {
                    '$project': {
                        'products': 0
                    }
                }
            ]
            if storages or user_allowed_storages:
                pipe_lines[6]['$match']["storage_id"] = {"$in": storages if storages else user_allowed_storages}
            result = mongo.product.aggregate(pipe_lines + [{"$limit": 50}])

            product_list = list()
            for res in result:
                if None in res['images']:
                    res['images'].remove(None)
                res['image'] = res['images'][0] if res['images'] else None
                res['name'] = res['name'].split(" | ")[0]
                del res['images']
                prices_list = list()
                if user_allowed_storages:
                    for sys_code in res['prices']:
                        for price in sys_code['prices']:
                            if price['storage_id'] in user_allowed_storages:
                                prices_list.append(price)
                else:
                    for sys_code in res['prices']:
                        for price in sys_code['prices']:
                            prices_list.append(price)

                prices_list.sort(key=lambda x: x["regular"])
                price, special_price = prices_list[0]["regular"], prices_list[0].get("special")
                res['price'] = price
                res['special_price'] = special_price
                del res['prices']

                product_list.append(res)

            return {"products": product_list, "storages_list": storages_labels}

    @staticmethod
    def get_category_list(user_allowed_storages, customer_type):
        with MongoConnection() as mongo:
            result = mongo.product.aggregate([
                {
                    '$match': {
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'price': {
                            'storage_id': '$zz.k',
                            'regular': '$zz.v.regular',
                            'special': {
                                '$cond': [
                                    {
                                        '$and': [
                                            {
                                                '$gt': [
                                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                    '$zz.v.special_from_date'
                                                ]
                                            }, {
                                                '$lt': [
                                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                    '$zz.v.special_to_date'
                                                ]
                                            }
                                        ]
                                    }, '$zz.v.special', None
                                ]
                            }
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': dict({
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }
                    }, **({"storage_id": {"$in": user_allowed_storages}} if user_allowed_storages else {}))
                }, {
                    '$group': {
                        '_id': '$_id',
                        'item': {
                            '$addToSet': '$root_obj'
                        },
                        'prices': {
                            '$addToSet': '$price'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'item': {
                            '$first': '$item'
                        },
                        'prices': 1
                    }
                }, {
                    '$facet': {
                        'categories': [
                            {
                                '$project': {
                                    'item.system_code': {
                                        '$substr': [
                                            '$item.system_code', 0, 6
                                        ]
                                    },
                                    'item.sub_category': 1
                                }
                            }, {
                                '$group': {
                                    '_id': None,
                                    'categories': {
                                        '$addToSet': '$item'
                                    }
                                }
                            }, {
                                '$sort': {
                                    'categories.system_code': 1
                                }
                            }
                        ],
                        'brands': [
                            {
                                '$match': {
                                    'item.sub_category': 'Mobile'
                                }
                            }, {
                                '$project': {
                                    'item.system_code': {
                                        '$substr': [
                                            '$item.system_code', 0, 9
                                        ]
                                    },
                                    'item.brand': 1
                                }
                            }, {
                                '$group': {
                                    '_id': None,
                                    'brands': {
                                        '$addToSet': '$item'
                                    }
                                }
                            }
                        ],
                        'latest_samsungs': [
                            {
                                '$match': {
                                    'item.brand': 'Samsung'
                                }
                            }, {
                                '$sort': {
                                    'date': 1
                                }
                            }, {
                                '$project': {
                                    'system_code': '$item.system_code',
                                    'name': '$item.name',
                                    'color': '$item.color',
                                    'attributes': '$item.attributes',
                                    'prices': 1
                                }
                            }, {
                                '$group': {
                                    '_id': {
                                        '$substr': [
                                            '$system_code', 0, 16
                                        ]
                                    },
                                    'name': {
                                        '$first': '$name'
                                    },
                                    'products': {
                                        '$push': '$$ROOT'
                                    },
                                    'prices': {
                                        '$push': {
                                            'system_code': '$system_code',
                                            'prices': '$prices'
                                        }
                                    }
                                }
                            }, {
                                '$project': {
                                    '_id': 0,
                                    'products': 1,
                                    'name': 1,
                                    'system_code': '$_id',
                                    'color': {
                                        '$setIntersection': {
                                            '$reduce': {
                                                'input': '$products',
                                                'initialValue': [],
                                                'in': {
                                                    '$concatArrays': [
                                                        '$$value', [
                                                            '$$this.color'
                                                        ]
                                                    ]
                                                }
                                            }
                                        }
                                    },
                                    'images': {
                                        '$setIntersection': {
                                            '$reduce': {
                                                'input': '$products',
                                                'initialValue': [],
                                                'in': {
                                                    '$concatArrays': [
                                                        '$$value', [
                                                            '$$this.attributes.mainImage-pd'
                                                        ]
                                                    ]
                                                }
                                            }
                                        }
                                    },
                                    'prices': 1
                                }
                            }, {
                                '$project': {
                                    'products': 0
                                }
                            }, {
                                '$limit': 10
                            }
                        ]
                    }
                }
            ])
            result = result.next() if result.alive else None
            if result:
                categories = result.get("categories")[0].get("categories") if result.get("categories") else []
                categories = sorted(categories, key=lambda x: x['system_code'], reverse=False)
                mobile_brands = result.get("brands")[0].get("brands") if result.get("brands") else []
                latest_samsungs = result.get("latest_samsungs") if result.get("latest_samsungs") else []

                latest_samsungs_list = list()
                for res in latest_samsungs:
                    if None in res['images']:
                        res['images'].remove(None)
                    res['image'] = res['images'][0] if res['images'] else None
                    res['name'] = res['name'].split(" | ")[0]
                    del res['images']
                    prices_list = list()
                    if user_allowed_storages:
                        for sys_code in res['prices']:
                            for price in sys_code['prices']:
                                if price['storage_id'] in user_allowed_storages:
                                    prices_list.append(price)
                    else:
                        for sys_code in res['prices']:
                            for price in sys_code['prices']:
                                prices_list.append(price)

                    prices_list.sort(key=lambda x: x["regular"])
                    price, special_price = prices_list[0]["regular"], prices_list[0].get("special")
                    res['price'] = price
                    res['special_price'] = special_price
                    del res['prices']

                    latest_samsungs_list.append(res)

                for category in categories:
                    kowsar_data = mongo.kowsar_collection.find_one({"system_code": category.get('system_code')})
                    kowsar_data = kowsar_data if kowsar_data else {}
                    category['label'] = kowsar_data.get('sub_category_label') if kowsar_data.get(
                        "sub_category_label") else category.get('sub_category')
                    category['image'] = kowsar_data.get("image")

                for mobile_brand in mobile_brands:
                    kowsar_data = mongo.kowsar_collection.find_one({"system_code": mobile_brand.get('system_code')})
                    kowsar_data = kowsar_data if kowsar_data else {}
                    mobile_brand['label'] = kowsar_data.get('brand_label') if kowsar_data.get(
                        "brand_label") else mobile_brand.get('brand')
                    mobile_brand['image'] = kowsar_data.get("image")

                return {"categories": categories, "mobile_brands": mobile_brands,
                        "latest_samsungs": latest_samsungs_list}
            return False

    @staticmethod
    def get_product_page(system_code, user_allowed_storages, customer_type, lang, credit):
        with MongoConnection() as mongo:
            result = mongo.product.aggregate([
                {
                    '$match': {
                        'system_code': {
                            '$regex': f'^{system_code}'
                        },
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': dict({
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }
                    }, **({} if not user_allowed_storages else {
                        "storage_id": {"$in": user_allowed_storages}}))
                }, {
                    '$group': {
                        '_id': '$_id',
                        "storage_ids": {"$addToSet": "$storage_id"},
                        'item': {
                            '$addToSet': '$root_obj'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        "storage_ids": 1,
                        'item': {
                            '$first': '$item'
                        }
                    }
                }, {
                    '$project': {
                        'item': {
                            'system_code': 1,
                            'attributes': 1,
                            'color': 1,
                            'guaranty': 1,
                            'name': 1,
                            'seller': 1,
                            "brand": 1,
                            'main_category': 1,
                            'model': 1,
                            "GIN": 1,
                            'sub_category': 1,
                        },
                        'warehouse_details': {
                            '$filter': {
                                'input': {
                                    '$objectToArray': f'$item.warehouse_details.{customer_type}.storages'
                                },
                                'as': 'storage_item',
                                'cond': {
                                    '$in': ['$$storage_item.k', "$storage_ids"]
                                }
                            }
                        }
                    }
                }, {
                    '$unwind': '$warehouse_details'
                }, {
                    '$project': {
                        'item': 1,
                        'warehouse_details.v': {
                            'storage_id': 1,
                            'min_qty': 1,
                            'max_qty': {
                                '$cond': [
                                    {
                                        '$gt': [
                                            '$warehouse_details.v.quantity', '$warehouse_details.v.max_qty'
                                        ]
                                    }, '$warehouse_details.v.max_qty', '$warehouse_details.v.quantity'
                                ]
                            },
                            'price': '$warehouse_details.v.regular',
                            'special_price': {
                                '$cond': [
                                    {
                                        '$and': [
                                            {
                                                '$gt': [
                                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                    '$warehouse_details.v.special_from_date'
                                                ]
                                            }, {
                                                '$lt': [
                                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                    '$warehouse_details.v.special_to_date'
                                                ]
                                            }
                                        ]
                                    }, '$warehouse_details.v.special', None
                                ]
                            },
                            "credit": {"$ifNull": ["$warehouse_details.v.credit" if credit else None, None]},
                            'warehouse_state': 1,
                            'warehouse_city': 1,
                            'warehouse_state_id': 1,
                            'warehouse_city_id': 1,
                            'warehouse_label': 1
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$item.system_code',
                        'item': {
                            '$addToSet': '$item'
                        },
                        'a': {
                            '$push': '$warehouse_details.v'
                        }
                    }
                }, {
                    '$project': {
                        'item': {
                            '$first': '$item'
                        },
                        'a': 1
                    }
                }, {
                    '$project': {
                        'item': {
                            'system_code': 1,
                            'attributes': 1,
                            'color': 1,
                            'guaranty': 1,
                            'name': 1,
                            'seller': 1,
                            "brand": 1,
                            'main_category': 1,
                            'model': 1,
                            'sub_category': 1,
                            "GIN": 1,
                            'warehouse_details': '$a'
                        }
                    }
                }, {
                    '$sort': {
                        '_id': 1
                    }
                }, {
                    '$group': {
                        '_id': None,
                        'products': {
                            '$push': '$item'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'products': 1,
                        'name': {
                            '$first': '$products.name'
                        }
                    }
                }
            ])
            product_result = result.next() if result.alive else {}
            if product_result:
                product_result["name"] = product_result['name'].split(" | ")[0]

                attributes_data = list(mongo.attributes_collection.find(
                    {}, {
                        "_id": 0,
                        "name": 1,
                        "ecommerce_use_in_filter": 1,
                        "ecommerce_use_in_search": 1,
                        "editable_in_ecommerce": 1,
                        "editable_in_portal": 1,
                        "label": 1,
                        "values": 1,
                        "portal_use_in_filter": 1,
                        "portal_use_in_search": 1,
                        "show_in_ecommerce": 1,
                        "show_in_portal": 1,
                        "priority": 1
                    }
                ))
                with RedisConnection() as redis:
                    for product in product_result['products']:
                        attributes_list = list()

                        for key, value in product.get("attributes", {}).items():
                            stored_data = copy([attr for attr in attributes_data if attr['name'] == key][0])
                            stored_data['value'] = value if not stored_data.get(
                                "values") else [attr_value.get("label") for attr_value in stored_data['values']
                                                if attr_value.get("value") == value][0] if value else None
                            if stored_data.get("values"):
                                del stored_data['values']
                            attributes_list.append(stored_data)

                        product['attributes'] = sorted(attributes_list, key=lambda x: x.get("priority", 9999))
                        product['color'] = {"value": product['color'],
                                            "label": redis.client.hget(product['color'], lang),
                                            "hex": redis.client.hget(product['color'], "hex")
                                            }
                        product['guaranty'] = {"value": product['guaranty'],
                                               "label": redis.client.hget(product['guaranty'], lang)}
                        product['seller'] = {"value": product['seller'],
                                             "label": redis.client.hget(product['seller'], lang)}
                        product['brand'] = {"value": product['brand'],
                                            "label": product['brand']}
                        product['main_category'] = {"value": product['main_category'],
                                                    "label": product['main_category']}
                        product['model'] = {"value": product['model'],
                                            "label": product['model']}
                        product['sub_category'] = {"value": product['sub_category'],
                                                   "label": product['sub_category']}

                kowsar_data = mongo.kowsar_collection.find_one({"system_code": system_code}, {"_id": 0})
                product_result.update({
                    "routes": {
                        "route": kowsar_data.get('main_category'),
                        "label": kowsar_data.get('main_category_label'),
                        "system_code": system_code[:2],
                        "child": {
                            "route": kowsar_data.get('sub_category'),
                            "label": kowsar_data.get('sub_category_label'),
                            "system_code": system_code[:6],
                            "child": {
                                "route": kowsar_data.get('brand'),
                                "label": kowsar_data.get('brand_label'),
                                "system_code": system_code[:9]
                            }
                        }
                    }
                })

                return product_result
            return False

    @staticmethod
    def get_product_list_by_system_code(system_code, page, per_page, storages, user_allowed_storages, customer_type):
        with MongoConnection() as mongo:
            def db_data_getter(query):
                db_data = mongo.kowsar_collection.find_one(query, {"_id": 0})
                return db_data if db_data else {}

            warehouses_query = dict({"isActive": True}, **(
                {} if not user_allowed_storages else {
                    "warehouse_id": {"$in": list(map(int, user_allowed_storages))}}))
            storages_labels = list(
                mongo.warehouses.find(warehouses_query,
                                      {"_id": 0, "storage_id": {"$convert": {"input": "$warehouse_id", "to": "string"}},
                                       "label": "$warehouse_name"}))

            skips = per_page * (page - 1)
            brands_pipe_line = [
                {
                    '$match': {
                        'system_code': {
                            '$regex': f'^{system_code[:6]}'
                        },
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': {
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$_id',
                        'item': {
                            '$addToSet': '$root_obj'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'item': {
                            '$first': '$item'
                        }
                    }
                }, {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$item.system_code', 0, 16
                            ]
                        },
                        'items': {
                            '$addToSet': '$item'
                        }
                    }
                }, {
                    '$project': {
                        'item': {
                            '$first': '$items'
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$item.brand',
                        'count': {
                            '$sum': 1
                        }
                    }
                }, {
                    '$project': {
                        'brand': '$_id',
                        '_id': 0,
                        'count': 1
                    }
                }
            ]
            if storages or user_allowed_storages:
                brands_pipe_line[6]['$match']["storage_id"] = {"$in": storages if storages else user_allowed_storages}
            brands_list_db = mongo.product.aggregate(brands_pipe_line)
            brands_list_db = brands_list_db if brands_list_db.alive else []
            brands_list = list()
            for brand in brands_list_db:
                brand_data = db_data_getter(
                    {"brand": brand.get("brand"), "system_code": {"$regex": f"^{system_code[:6]}"}})
                brands_list.append({"name": brand.get("brand"), "label": brand_data.get("brand_label"),
                                    "image": brand_data.get("image"),
                                    "route": brand.get("brand").replace(" ", ""),
                                    "count": brand.get("count"),
                                    "system_code": brand_data.get("system_code"),
                                    })

            brands_list = sorted(brands_list, key=lambda x: x['system_code'], reverse=False)

            pipe_lines = [
                {
                    '$match': {
                        'system_code': {
                            '$regex': f'^{system_code}'
                        },
                        f'visible_in_site.{customer_type}': True
                    }
                }, {
                    '$project': {
                        'system_code': 1,
                        'keys': {
                            '$objectToArray': '$warehouse_details'
                        },
                        'root_obj': '$$ROOT'
                    }
                }, {
                    '$unwind': '$keys'
                }, {
                    '$project': {
                        'system_code': 1,
                        'customer_type': '$keys.k',
                        'zz': {
                            '$objectToArray': '$keys.v.storages'
                        },
                        'root_obj': 1
                    }
                }, {
                    '$unwind': '$zz'
                }, {
                    '$project': {
                        'system_code': 1,
                        'storage_id': '$zz.k',
                        'customer_type': 1,
                        'qty': {
                            '$subtract': [
                                '$zz.v.quantity', '$zz.v.reserved'
                            ]
                        },
                        'min': {
                            '$subtract': [
                                {
                                    '$subtract': [
                                        '$zz.v.quantity', '$zz.v.reserved'
                                    ]
                                }, '$zz.v.min_qty'
                            ]
                        },
                        'price': {
                            'storage_id': '$zz.k',
                            'regular': '$zz.v.regular',
                            'special': {
                                '$cond': [
                                    {
                                        '$and': [
                                            {
                                                '$gt': [
                                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                    '$zz.v.special_from_date'
                                                ]
                                            }, {
                                                '$lt': [
                                                    jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                    '$zz.v.special_to_date'
                                                ]
                                            }
                                        ]
                                    }, '$zz.v.special', None
                                ]
                            }
                        },
                        'root_obj': 1
                    }
                }, {
                    '$match': {
                        'customer_type': customer_type,
                        'qty': {
                            '$gt': 0
                        },
                        'min': {
                            '$gte': 0
                        }
                    }
                }, {
                    '$group': {
                        '_id': '$_id',
                        'item': {
                            '$addToSet': '$root_obj'
                        },
                        'prices': {
                            '$addToSet': '$price'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'item': {
                            '$first': '$item'
                        },
                        'prices': 1
                    }
                }, {
                    '$project': {
                        'system_code': '$item.system_code',
                        'name': '$item.name',
                        'color': '$item.color',
                        'attributes': '$item.attributes',
                        'prices': 1
                    }
                }, {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$system_code', 0, 16
                            ]
                        },
                        'name': {
                            '$first': '$name'
                        },
                        'products': {
                            '$push': '$$ROOT'
                        },
                        'prices': {
                            '$push': {
                                'system_code': '$system_code',
                                'prices': '$prices'
                            }
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'products': 1,
                        'name': 1,
                        'system_code': '$_id',
                        'color': {
                            '$setIntersection': {
                                '$reduce': {
                                    'input': '$products',
                                    'initialValue': [],
                                    'in': {
                                        '$concatArrays': [
                                            '$$value', [
                                                '$$this.color'
                                            ]
                                        ]
                                    }
                                }
                            }
                        },
                        'images': {
                            '$setIntersection': {
                                '$reduce': {
                                    'input': '$products',
                                    'initialValue': [],
                                    'in': {
                                        '$concatArrays': [
                                            '$$value', [
                                                '$$this.attributes.mainImage-pd'
                                            ]
                                        ]
                                    }
                                }
                            }
                        },
                        'prices': 1
                    }
                }, {
                    '$project': {
                        'products': 0
                    }
                }, {
                    "$sort": {
                        "name": 1
                    }
                }
            ]
            if storages or user_allowed_storages:
                pipe_lines[6]['$match']["storage_id"] = {"$in": storages if storages else user_allowed_storages}
            result = mongo.product.aggregate(pipe_lines + [{
                '$skip': skips
            }, {
                '$limit': per_page
            }])
            count_aggregate = mongo.product.aggregate(pipe_lines + [{
                '$count': 'count'
            }])
            products_count = count_aggregate.next().get("count", 0) if count_aggregate.alive else 0

            product_list = list()
            for res in result:
                if None in res['images']:
                    res['images'].remove(None)
                res['image'] = res['images'][0] if res['images'] else None
                res['name'] = res['name'].split(" | ")[0]
                del res['images']
                colors_list = list()
                with RedisConnection() as redis:
                    for color in res.get('color', []):
                        colors_list.append(redis.client.hget(color, "hex"))
                res['color'] = colors_list
                prices_list = list()
                if user_allowed_storages:
                    for sys_code in res['prices']:
                        for price in sys_code['prices']:
                            if price['storage_id'] in user_allowed_storages:
                                prices_list.append(price)
                else:
                    for sys_code in res['prices']:
                        for price in sys_code['prices']:
                            prices_list.append(price)

                prices_list.sort(key=lambda x: x["regular"])
                price, special_price = prices_list[0]["regular"], prices_list[0].get("special")
                res['price'] = price
                res['special_price'] = special_price
                del res['prices']

                product_list.append(res)

            return {"brands": brands_list, "products": product_list, "products_count": products_count,
                    "storages_list": storages_labels}

    @staticmethod
    def edit_product(system_code, data):
        # with MongoConnection() as mongo:
        #     visible_in_site = data.get("visible_in_site")
        #     result = mongo.product.update_one({"system_code": system_code, "step": 4},
        #                                       {"$set": {"visible_in_site": visible_in_site}})
        #     if result.modified_count or result.matched_count:
        #         return {"message": "product visibility updated successfully",
        #                 "label": "?????????? ?????????? ?????????? ???? ???????????? ?????????????????? ????"}
        #     return {"message": "product visibility update failed",
        #             "label": "?????????????????? ?????????? ?????????? ?????????? ???? ?????? ?????????? ????"}
        return {"message": "product visibility update failed",
                "label": "?????????????????? ?????????? ?????????? ?????????? ???? ?????? ?????????? ????"}

    @staticmethod
    def get_product_by_system_code(system_code, lang):
        with MongoConnection() as mongo:
            result = mongo.product.find_one({'system_code': system_code}, {"_id": 0})
            if result:
                attributes_data = list(mongo.attributes_collection.find(
                    {}, {
                        "_id": 0,
                        "name": 1,
                        "ecommerce_use_in_filter": 1,
                        "ecommerce_use_in_search": 1,
                        "editable_in_ecommerce": 1,
                        "editable_in_portal": 1,
                        "label": 1,
                        "portal_use_in_filter": 1,
                        "portal_use_in_search": 1,
                        "show_in_ecommerce": 1,
                        "show_in_portal": 1,
                    }
                ))

                attributes_list = list()

                for key, value in result.get("attributes", {}).items():
                    stored_data = [attr for attr in attributes_data if attr['name'] == key][0]
                    stored_data['value'] = value
                    attributes_list.append(stored_data)

                result['attributes'] = attributes_list
                with RedisConnection() as redis:
                    result['color'] = {"value": result['color'], "label": redis.client.hget(result['color'], lang)}
                    result['guaranty'] = {"value": result['guaranty'],
                                          "label": redis.client.hget(result['guaranty'], lang)}
                    result['seller'] = {"value": result['seller'], "label": redis.client.hget(result['seller'], lang)}

                kowsar_data = mongo.kowsar_collection.find_one({"system_code": system_code[:9]}, {"_id": 0})
                result['sub_category'] = {"value": result['sub_category'],
                                          "label": kowsar_data.get('sub_category_label') if kowsar_data else None}
                result['main_category'] = {"value": result['main_category'],
                                           "label": kowsar_data.get('main_category_label') if kowsar_data else None}
                result['brand'] = {"value": result['brand'],
                                   "label": kowsar_data.get('brand_label') if kowsar_data else None}

                result.update({
                    "routes": {
                        "route": result.get('main_category'),
                        "label": kowsar_data.get('main_category_label'),
                        "system_code": system_code[:2],
                        "child": {
                            "route": result.get('sub_category'),
                            "label": kowsar_data.get('sub_category_label'),
                            "system_code": system_code[:6],
                            "child": {
                                "route": result.get('brand'),
                                "label": kowsar_data.get('brand_label'),
                                "system_code": system_code[:9]
                            }
                        }
                    }
                })

                return result
            return None

    def create(self):
        with MongoConnection() as mongo:
            result = mongo.product.insert_many(self.products)

            mongo.kowsar_collection.update_many(
                {"system_code": {"$in": [system_code.get("system_code") for system_code in self.products]}},
                {"$set": {"created": True}}
            )

            if result.inserted_ids:
                return True
            return False

    def make_product_obj(self):
        products = list()
        for system_code in self.system_codes:
            data = KowsarGetter.system_code_name_getter(system_code)
            if data:
                data['name'] = self.name
                data['url_name'] = self.url_name
                data['step'] = 1
                products.append(data)
                self.products = products
                return True
            return False

    @staticmethod
    def get_product_attributes(system_code):
        with MongoConnection() as mongo:
            result = mongo.product.find_one({"system_code": system_code}, {"_id": 0})
            if result:
                out_data = {
                    "name": result.get("name"),
                    "system_code": result.get("system_code"),
                    "brand": result.get("brand"),
                    "mainCategory": result.get("main_category"),
                    "model": result.get("model"),
                    "subCategory": result.get("sub_category"),
                    "configs": " ".join(result.get("configs", {}).values()),
                    "seller": result.get("seller"),
                    "color": result.get("color"),
                    "guaranty": result.get("guaranty"),
                    "attributes": list()
                }

                db_attribute = mongo.attributes_collection.aggregate([
                    {
                        '$project': {
                            '_id': 0,
                            'item': '$$ROOT',
                            'result': {
                                '$cond': {
                                    'if': {
                                        '$eq': [
                                            '$set_to_nodes', True
                                        ]
                                    },
                                    'then': {
                                        '$eq': [
                                            '$parent', {
                                                '$substr': [
                                                    system_code, 0, {
                                                        '$strLenCP': '$parent'
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    'else': {
                                        '$eq': [
                                            '$system_code', system_code
                                        ]
                                    }
                                }
                            }
                        }
                    }, {
                        '$match': {
                            'result': True
                        }
                    }, {
                        '$project': {
                            'result': 0,
                            'item._id': 0
                        }
                    }
                ])

                if db_attribute:
                    for attr in db_attribute:
                        attribute = attr.get("item")
                        for stored_attrs in result.get("attributes", []):
                            if attribute.get("name") == stored_attrs:
                                attribute["value"] = result.get("attributes", {}).get(stored_attrs)
                                break
                        out_data['attributes'].append(attribute)
                    return out_data, True
                return "attribute not found", False
            return "product not found", False

    @staticmethod
    def get_product_backoffice(system_code):
        with MongoConnection() as mongo:
            result = mongo.product.find_one({"system_code": system_code}, {"_id": 0})
            if result:
                return result
            return None

    @staticmethod
    def set_product_price(system_code, customer_type):
        with MongoConnection() as mongo:
            result = mongo.product.update_one({"system_code": system_code}, {"$set": {"price": customer_type}})
            if result.modified_count:
                return True
            return False

    @staticmethod
    def get_product_list_back_office(brands, warehouses, price_from, price_to, sellers, colors,
                                     quantity_from, quantity_to, date_from, date_to, guarantees, steps,
                                     visible_in_site, approved, available, page, per_page, system_code, lang):
        with MongoConnection() as mongo:
            skip = (page - 1) * per_page
            pipe_lines = [
                {
                    '$facet': {
                        'list': [
                            {
                                '$match': {}
                            }, {
                                '$project': {
                                    'system_code': 1,
                                    'keys': {
                                        '$objectToArray': '$warehouse_details'
                                    },
                                    'root_obj': '$$ROOT'
                                }
                            }, {
                                '$unwind': '$keys'
                            }, {
                                '$project': {
                                    'system_code': 1,
                                    'customer_type': '$keys.k',
                                    'zz': {
                                        '$objectToArray': '$keys.v.storages'
                                    },
                                    'root_obj': 1
                                }
                            }, {
                                '$unwind': '$zz'
                            }, {
                                '$project': {
                                    'system_code': 1,
                                    'storage_id': '$zz.k',
                                    'customer_type': 1,
                                    'quantity': '$zz.v.quantity',
                                    'price': {
                                        'storage_id': '$zz.k',
                                        'regular': '$zz.v.regular',
                                        'special': '$zz.v.special'
                                    },
                                    'root_obj': 1
                                }
                            }, {
                                '$match': {}
                            }, {
                                '$group': {
                                    '_id': '$_id',
                                    'item': {
                                        '$addToSet': '$root_obj'
                                    }
                                }
                            }, {
                                '$project': {
                                    '_id': 0,
                                    'item': {
                                        '$first': '$item'
                                    }
                                }
                            }, {
                                '$group': {
                                    '_id': {
                                        '$substr': [
                                            '$item.system_code', 0, 16
                                        ]
                                    },
                                    'name': {
                                        '$first': '$item.name'
                                    },
                                    'products': {
                                        '$push': '$item'
                                    }
                                }
                            }, {
                                '$project': {
                                    '_id': 0,
                                    'products': 1,
                                    'name': {
                                        '$first': {
                                            '$split': [
                                                '$name', ' | '
                                            ]
                                        }
                                    },
                                    'system_code': '$_id'
                                }
                            }, {
                                '$project': {
                                    'products._id': 0
                                }
                            },
                            {
                                "$sort": {
                                    "system_code": 1
                                }
                            },
                            {
                                '$skip': skip
                            }, {
                                '$limit': per_page
                            }
                        ],
                        'filters': [
                            {
                                '$group': {
                                    '_id': None,
                                    'brands': {
                                        '$addToSet': '$brand'
                                    },
                                    'sellers': {
                                        '$addToSet': '$seller'
                                    },
                                    'colors': {
                                        '$addToSet': '$color'
                                    },
                                    'guaranties': {
                                        '$addToSet': '$guaranty'
                                    },
                                    'steps': {
                                        '$addToSet': '$step'
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
            if system_code:
                pipe_lines[0]['$facet']['list'][0]['$match']['system_code'] = {"$regex": f"^{system_code}"}
            if brands:
                pipe_lines[0]['$facet']['list'][0]['$match']['brand'] = {'$in': brands}
            if sellers:
                pipe_lines[0]['$facet']['list'][0]['$match']['seller'] = {'$in': sellers}
            if colors:
                pipe_lines[0]['$facet']['list'][0]['$match']['color'] = {'$in': colors}
            if guarantees:
                pipe_lines[0]['$facet']['list'][0]['$match']['guaranty'] = {'$in': guarantees}
            if steps:
                pipe_lines[0]['$facet']['list'][0]['$match']['step'] = {'$in': steps}
            if date_from or date_to:
                pipe_lines[0]['$facet']['list'][0]['$match']['date'] = {}
                if date_to:
                    pipe_lines[0]['$facet']['list'][0]['$match']['date']['$lte'] = date_to
                if date_from:
                    pipe_lines[0]['$facet']['list'][0]['$match']['date']['$gte'] = date_from
            if price_from or price_to:
                pipe_lines[0]['$facet']['list'][6]['$match']['price.regular'] = {}
                if price_to:
                    pipe_lines[0]['$facet']['list'][6]['$match']['price.regular']['$lte'] = price_to
                if price_from:
                    pipe_lines[0]['$facet']['list'][6]['$match']['price.regular']['$gte'] = price_from
            if quantity_to or quantity_from:
                pipe_lines[0]['$facet']['list'][6]['$match']['quantity'] = {}
                if quantity_to:
                    pipe_lines[0]['$facet']['list'][6]['$match']['quantity']['$lte'] = quantity_to
                if quantity_from:
                    pipe_lines[0]['$facet']['list'][6]['$match']['quantity']['$gte'] = quantity_from
            if warehouses:
                pipe_lines[0]['$facet']['list'][6]['$match']['storage_id'] = {'$in': warehouses}

            result = mongo.product.aggregate(pipe_lines)

            result = result.next() if result else {}

            brands = result.get("filters", [{}])[0].get("brands", [])
            sellers = result.get("filters", [{}])[0].get("sellers", [])
            colors = result.get("filters", [{}])[0].get("colors", [])
            guaranties = result.get("filters", [{}])[0].get("guaranties", [])
            steps = result.get("filters", [{}])[0].get("steps", [])

            total_products = mongo.product.aggregate(pipe_lines[0]['$facet']['list'][:-2] + [{"$count": "count"}])
            total_products = total_products.next().get("count", 0) if total_products.alive else 0

            products_list = result.get("list", [])
            warehouses_list = list(mongo.warehouses.find({"isActive": True}, {"_id": 0,
                                                                              "storage_id": {
                                                                                  "$convert": {"input": "$warehouse_id",
                                                                                               "to": "string"}},
                                                                              "storage_label": "$warehouse_name",
                                                                              }))
            filters = [
                {
                    "name": "brands",
                    "label": "????????",
                    "input_type": "multi_select",
                    "options": brands
                },
                {
                    "name": "colors",
                    "label": "??????",
                    "input_type": "multi_select",
                    "options": colors
                },
                {
                    "name": "price",
                    "label": "????????",
                    "input_type": "range",
                },
                {
                    "name": "warehouse",
                    "label": "??????????",
                    "input_type": "multi_select",
                    "options": warehouses_list
                },
                {
                    "name": "sellers",
                    "label": "??????????????",
                    "input_type": "multi_select",
                    "options": sellers
                },
                {
                    "name": "quantity",
                    "label": "??????????",
                    "input_type": "range",
                },
                {
                    "name": "date",
                    "label": "??????????",
                    "input_type": "date",
                },
                {
                    "name": "guarantees",
                    "label": "??????????????",
                    "input_type": "multi_select",
                    "options": guaranties
                },
                {
                    "name": "visible_in_site",
                    "label": "???????? ??????????",
                    "input_type": "checkbox",
                },
                {
                    "name": "approved",
                    "label": "?????????? ??????",
                    "input_type": "checkbox",
                },
                {
                    "name": "available",
                    "label": "??????????",
                    "input_type": "checkbox",
                },
                {
                    "name": "steps",
                    "label": "??????????",
                    "input_type": "multi_select",
                    "options": steps
                }
            ]
            if result:
                return {"filters": filters, "products": products_list, "total_products": total_products}
            return None


class Price:
    def __init__(self, system_code, customer_type):
        self.system_code = system_code
        self.customer_type = customer_type

    def system_code_exists(self):
        with MongoConnection() as mongo:
            result = mongo.product.find_one({"system_code": self.system_code})
            return True if result else False

    def set_product_price(self):
        with MongoConnection() as client:
            db_query = dict()
            warehouses = list(client.warehouses.find({}, {"_id": 0}))
            for key, value in self.customer_type.items():
                if value.get("storages"):
                    for storage_data in value.get("storages"):
                        storage_id = storage_data.get("storage_id")
                        obj = [i for i in warehouses if str(i['warehouse_id']) == storage_id]
                        storage_data.update(
                            {"warehouse_state": obj[0].get("state"), "warehouse_city": obj[0].get("city"),
                             "warehouse_state_id": obj[0].get("state_id"),
                             "warehouse_city_id": obj[0].get("city_id"),
                             "warehouse_label": obj[0].get("warehouse_name"),
                             })
                        for storage_keys, storage_value in storage_data.items():
                            db_query.update(
                                {f"warehouse_details.{key}.storages.{storage_id}.{storage_keys}": storage_value})
                else:
                    db_query.update({
                        f"warehouse_details.{key}.type": key
                    })

            db_query.update({
                "step": {"$cond": [{"$eq": ["$step", 2]}, 3, "$step"]}
            })

            result = client.product.update_one({"system_code": self.system_code}, [{"$set": db_query}])

            if result.modified_count:
                return True
            return None

    @staticmethod
    def update_price(system_code: str, customer_type: str, storage_id: str, regular: int, special: int,
                     informal_price: dict, credit: dict,
                     special_from_date: str, special_to_date: str) -> Union[str, None]:
        with MongoConnection() as client:
            update_data = {f"warehouse_details.{customer_type}.storages.{storage_id}.storage_id": storage_id}
            if regular:
                update_data.update({
                    f"warehouse_details.{customer_type}.storages.{storage_id}.regular": regular
                })
            if special is not None:
                update_data.update({
                    f"warehouse_details.{customer_type}.storages.{storage_id}.special": special
                })
            if informal_price:
                update_data.update({
                    f"warehouse_details.{customer_type}.storages.{storage_id}.informal_price": informal_price
                })
            if credit:
                update_data.update({
                    f"warehouse_details.{customer_type}.storages.{storage_id}.credit": credit
                })
            if special_from_date:
                update_data.update({
                    f"warehouse_details.{customer_type}.storages.{storage_id}.special_from_date": special_from_date
                })
            if special_to_date:
                update_data.update({
                    f"warehouse_details.{customer_type}.storages.{storage_id}.special_to_date": special_to_date
                })
            warehouses = list(client.warehouses.find({}, {"_id": 0}))
            obj = [i for i in warehouses if str(i['warehouse_id']) == storage_id]
            update_data.update(
                {f"warehouse_details.{customer_type}.storages.{storage_id}.warehouse_state": obj[0].get("state"),
                 "warehouse_city": obj[0].get("city"),
                 f"warehouse_details.{customer_type}.storages.{storage_id}.warehouse_state_id": obj[0].get("state_id"),
                 f"warehouse_details.{customer_type}.storages.{storage_id}.warehouse_city_id": obj[0].get("city_id"),
                 f"warehouse_details.{customer_type}.storages.{storage_id}.warehouse_label": obj[0].get(
                     "warehouse_name"),
                 })

            update_data.update({
                "step": {"$cond": [{"$eq": ["$step", 2]}, 3, "$step"]}
            })

            result = client.product.update_one({"system_code": system_code}, [{"$set": update_data}])

            if result.modified_count:
                return "???????? ???? ???????????? ?????????? ????"
            return None


class Quantity:

    def __init__(self, system_code, customer_types):
        self.system_code = system_code
        self.customer_types = customer_types

    @staticmethod
    def get_stock(system_code: str) -> dict:
        """
        get physical stock of products
        """
        with MongoConnection() as client:
            db_stocks = []
            result = {
                "total": 0,
                "storages": []
            }
            for stock in db_stocks:
                quantity = stock["quantity"] - stock["reserve"]
                result["total"] += quantity
                wearhouses = client.warehouses.find_one({"warehouse_id": int(stock["stockId"])}, {"_id": 0})
                result["storages"].append({"storage_id": stock["stockId"],
                                           "storage_label": wearhouses["warehouse_name"],
                                           "stock": quantity})
            return result

    def set_quantity(self):
        with MongoConnection() as client:
            client.quantity_log.insert_one({
                "system_code": self.system_code, "customer_types": self.customer_types,
                "time": jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            db_query = dict()
            for key, value in self.customer_types.items():
                if value.get("storages"):
                    for storage_data in value.get("storages"):
                        storage_id = storage_data.get("storage_id")
                        for storage_keys, storage_value in storage_data.items():
                            db_query.update(
                                {f"warehouse_details.{key}.storages.{storage_id}.{storage_keys}": storage_value})
                        db_query.update(
                            {f"warehouse_details.{key}.storages.{storage_id}.reserved": {
                                "$cond": [{"$ne": [f"$warehouse_details.{key}.storages.{storage_id}.reserved", None]},
                                          0, f"$warehouse_details.{key}.storages.{storage_id}.reserved"]}})

                else:
                    db_query.update({
                        f"warehouse_details.{key}.type": key
                    })

            db_query.update({
                "step": {"$cond": [{"$eq": ["$step", 3]}, 4, "$step"]}
            })

            result = client.product.update_one({"system_code": self.system_code}, [{"$set": db_query}])

            if result.modified_count:
                return True
            return None

    @staticmethod
    def get_all_stocks():
        """
        get all stocks
        """
        with MongoConnection() as client:
            return list(client.warehouses.find({"isActive": True}, {"_id": 0,
                                                                    "storage_id": "$warehouse_id",
                                                                    "storage_label": "$warehouse_name",
                                                                    }))

    @staticmethod
    def update_quantity(system_code: str, customer_type: str, storage_id: str, quantity: int,
                        min_qty: int, max_qty: int) -> Union[str, None]:
        """
        update quantity in database
        """
        with MongoConnection() as client:
            client.quantity_log.insert_one({
                "system_code": system_code, "customer_type": customer_type, "storage_id": storage_id,
                "quantity": quantity,
                "min_qty": min_qty, "max_qty": max_qty,
                "time": jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            storage = {
                "storage_id": storage_id,
                "quantity": quantity,
                "min_qty": min_qty,
                "max_qty": max_qty
            }
            warehouses = list(client.warehouses.find({}, {"_id": 0}))
            obj = [i for i in warehouses if str(i['warehouse_id']) == storage['storage_id']]
            storage.update({"warehouse_state": obj[0].get("state"), "warehouse_city": obj[0].get("city"),
                            "warehouse_state_id": obj[0].get("state_id"),
                            "warehouse_city_id": obj[0].get("city_id"),
                            "warehouse_label": obj[0].get("warehouse_name"),
                            })
            db_query = {f"warehouse_details.{customer_type}.storages.{storage_id}.{key}": value for key, value in
                        storage.items() if value is not None}

            db_query.update({
                "step": {"$cond": [{"$eq": ["$step", 3]}, 4, "$step"]}
            })

            result = client.product.update_one({"system_code": system_code}, [{"$set": db_query}])

            if result.modified_count:
                return '???????????? ???? ???????????? ?????????? ????'
            return None

    @staticmethod
    def get_quantity_list(products_list):
        """
        get quantity from databases for checkout
        """
        result = []
        checkout_pass = True
        for data in products_list:
            # check salable in stocks and quantity
            check_result = check_quantity(data)
            # msm_check = check_result.check_stocks()
            product_quantity_check = check_result.check_quantity()
            price_check_result = check_result.check_price()
            if data['price'] != price_check_result:
                data['new_price'] = price_check_result
            # system code not found in sms stocks
            if not product_quantity_check:
                checkout_pass = False
                data['quantity_checkout'] = "system code not found"
                result.append(data)

            else:
                # # if salable in msm_stocks and products quantity is equal
                # if msm_check == product_quantity_check:
                #     try:
                #         if data['count'] <= product_quantity_check:
                #             data['quantity_checkout'] = "pass"
                #             result.append(data)
                #         else:
                #             checkout_pass = False
                #             data['quantity_checkout'] = "edited"
                #             data['new_quantity'] = product_quantity_check
                #             result.append(data)
                #     except:
                #         checkout_pass = False
                #         data['quantity_checkout'] = "system code not found"
                #         result.append(data)
                #
                # # if salable in msm_stocks and products quantity is not equal we chose products
                # else:
                try:
                    if data['count'] <= product_quantity_check:
                        data['quantity_checkout'] = "pass"
                        result.append(data)
                    else:
                        checkout_pass = False
                        data['quantity_checkout'] = "edited"
                        data['new_quantity'] = product_quantity_check

                        result.append(data)
                except:
                    checkout_pass = False
                    data['quantity_checkout'] = "system code not found"
                    result.append(data)

        if checkout_pass:
            return result, True
        else:
            return result, False


class AddAttributes:
    def __init__(self, system_code, attributes):
        self.system_code = system_code
        self.attributes = attributes

    def system_code_exists(self) -> bool:
        with MongoConnection() as mongo:
            result = mongo.product.find_one({'system_code': self.system_code})
            return True if result else False

    def create(self) -> tuple:
        with MongoConnection() as mongo:
            stored_data = mongo.product.find_one({"system_code": self.system_code, }, {"_id": 0})
            db_action = {"$set": {"attributes": self.attributes}}
            if stored_data.get("step") == 1:
                db_action["$set"]["step"] = 2

            result = mongo.product.update_one({"system_code": self.system_code}, db_action)
            if result.modified_count:
                return {"message": "attribute added successfully", "label": "?????? ???? ???????????? ?????????? ????"}, True
            return {"error": "attribute add failed", "label": "???????????? ???????????? ?????? ???? ???????? ????????????"}, False
