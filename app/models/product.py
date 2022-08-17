import re
from typing import Union

import jdatetime

from app.helpers.mongo_connection import MongoConnection
from app.helpers.redis_connection import RedisConnection
from app.modules.kowsar_getter import KowsarGetter
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
    def system_code_exists(system_code):
        with MongoConnection() as mongo:
            result = mongo.product.find_one({"system_code": system_code})
            return True if result else False

    @staticmethod
    def search_product_child(name, system_code, storages, customer_type):

        with MongoConnection() as mongo:
            pipe_lines = [
                {
                    '$match': {
                        'visible_in_site': True
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
                        },
                        'storage_id': {
                            '$in': storages
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
                },
                {
                    '$project': {
                        'item._id': 0
                    }
                }
                , {
                    '$replaceRoot': {
                        'newRoot': '$item'
                    }
                }
            ]
            if not system_code:
                pipe_lines[0]['$match']['name'] = {'$regex': re.compile(fr"{name}(?i)")}
            else:
                pipe_lines[0]['$match']['system_code'] = system_code

            result = mongo.product.aggregate(pipe_lines)
            return list(result)

    @staticmethod
    def get_product_by_name(name, user_allowed_storages, customer_type):
        with MongoConnection() as mongo:
            warehouses = list(mongo.warehouses_collection.find({}, {"_id": 0}))
            storages_labels = list()
            for allowed_storage in user_allowed_storages:
                obj = [i for i in warehouses if str(i['warehouse_id']) == allowed_storage]
                storages_labels.append({
                    "storage_id": allowed_storage,
                    "label": obj[0]['warehouse_name'] if obj else None
                })
            pipe_lines = [
                {
                    '$match': {
                        'name': {
                            '$regex': re.compile(rf"{name}(?i)")
                        },
                        'visible_in_site': True
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
                        "storage_id": {"$in": user_allowed_storages}
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
                        'visible_in_site': True
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
                        },
                        "storage_id": {"$in": user_allowed_storages}
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
                    '$facet': {
                        'categories': [
                            {
                                '$match': {
                                    'item.sub_category': {
                                        '$in': [
                                            'Mobile', 'Tablet'
                                        ]
                                    }
                                }
                            }, {
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
    def get_product_page(system_code, user_allowed_storages, customer_type, lang):
        with MongoConnection() as mongo:
            result = mongo.product.aggregate([
                {
                    '$match': {
                        'system_code': {
                            '$regex': f'^{system_code}'
                        },
                        'visible_in_site': True
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
                        },
                        "storage_id": {"$in": user_allowed_storages}
                    }
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
                            'seller': 1
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
                            '$addToSet': '$warehouse_details.v'
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
                            'warehouse_details': '$a'
                        }
                    }
                }, {
                    '$group': {
                        '_id': {
                            '$substr': [
                                '$system_code', 0, 16
                            ]
                        },
                        'products': {
                            '$addToSet': '$item'
                        }
                    }
                }, {
                    '$project': {
                        '_id': 0,
                        'products': 1,
                        'name': {
                            '$first': '$products'
                        }
                    }
                }, {
                    '$project': {
                        'name': '$name.name',
                        'products': 1
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
                        "portal_use_in_filter": 1,
                        "portal_use_in_search": 1,
                        "show_in_ecommerce": 1,
                        "show_in_portal": 1,
                    }
                ))
                with RedisConnection() as redis:
                    for product in product_result['products']:
                        attributes_list = list()

                        for key, value in product.get("attributes", {}).items():
                            stored_data = [attr for attr in attributes_data if attr['name'] == key][0]
                            stored_data['value'] = value
                            attributes_list.append(stored_data)

                        product['attributes'] = attributes_list
                        product['color'] = {"value": product['color'],
                                            "label": redis.client.hget(product['color'], lang)}
                        product['guaranty'] = {"value": product['guaranty'],
                                               "label": redis.client.hget(product['guaranty'], lang)}
                        product['seller'] = {"value": product['seller'],
                                             "label": redis.client.hget(product['seller'], lang)}

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
    def get_product_list_by_system_code(system_code, page, per_page, user_allowed_storages, customer_type):
        with MongoConnection() as mongo:
            def db_data_getter(query):
                result = mongo.kowsar_collection.find_one(query, {"_id": 0})
                return result if result else {}

            warehouses = list(mongo.warehouses_collection.find({}, {"_id": 0}))
            storages_labels = list()
            for allowed_storage in user_allowed_storages:
                obj = [i for i in warehouses if str(i['warehouse_id']) == allowed_storage]
                storages_labels.append({
                    "storage_id": allowed_storage,
                    "label": obj[0]['warehouse_name'] if obj else None
                })
            skips = per_page * (page - 1)
            brands_pipe_line = [
                {
                    '$match': {
                        'system_code': {
                            '$regex': f'^{system_code[:6]}'
                        },
                        'visible_in_site': True
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
                        },
                        "storage_id": {"$in": user_allowed_storages}
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
            brands_list_db = mongo.product.aggregate(brands_pipe_line)
            brands_list_db = brands_list_db if brands_list_db.alive else []
            brands_list = list()
            for brand in brands_list_db:
                brand_data = db_data_getter({"brand": brand.get("brand"), "system_code": {"$regex": "^.{9}$"}})
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
                        "visible_in_site": True
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
                        "storage_id": {"$in": user_allowed_storages}
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
        with MongoConnection() as mongo:
            visible_in_site = data.get("visible_in_site")
            result = mongo.product.update_one({"system_code": system_code, "step": 4},
                                              {"$set": {"visible_in_site": visible_in_site}})
            if result.modified_count or result.matched_count:
                return {"message": "product visibility updated successfully",
                        "label": "وضعیت نمایش محصول با موفقیت بروزرسانی شد"}
            return {"message": "product visibility update failed",
                    "label": "بروزرسانی وضعیت نمایش محصول با خطا مواجه شد"}

    @staticmethod
    def get_product_by_system_code(system_code, lang):
        with MongoConnection() as mongo:
            result = mongo.product.find_one({'system_code': system_code, "visible_in_site": True}, {"_id": 0})
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
                result['brand'] = {"value": result['brand'], "label": result['brand']}
                result['color'] = {"value": result['color'], "label": result['color']}
                result['guaranty'] = {"value": result['guaranty'], "label": result['guaranty']}
                result['main_category'] = {"value": result['main_category'], "label": result['main_category']}
                result['seller'] = {"value": result['seller'], "label": result['seller']}
                result['sub_category'] = {"value": result['sub_category'], "label": result['sub_category']}

                kowsar_data = mongo.kowsar_collection.find_one({"system_code": system_code}, {"_id": 0})
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
                                     visible_in_site, approved, available, page, per_page, lang):
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
            if visible_in_site:
                pipe_lines[0]['$facet']['list'][0]['$match']['visible_in_site'] = visible_in_site
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
            warehouses_list = list(mongo.warehouses_collection.find({"isActive": True}, {"_id": 0,
                                                                                         "storage_id": "$warehouse_id",
                                                                                         "storage_label": "$warehouse_name",
                                                                                         }))
            filters = [
                {
                    "name": "brands",
                    "label": "برند",
                    "input_type": "multi_select",
                    "options": brands
                },
                {
                    "name": "colors",
                    "label": "رنگ",
                    "input_type": "multi_select",
                    "options": colors
                },
                {
                    "name": "price",
                    "label": "قیمت",
                    "input_type": "range",
                },
                {
                    "name": "warehouse",
                    "label": "انبار",
                    "input_type": "multi_select",
                    "options": warehouses_list
                },
                {
                    "name": "sellers",
                    "label": "فروشنده",
                    "input_type": "multi_select",
                    "options": sellers
                },
                {
                    "name": "quantity",
                    "label": "تعداد",
                    "input_type": "range",
                },
                {
                    "name": "date",
                    "label": "تاریخ",
                    "input_type": "date",
                },
                {
                    "name": "guarantees",
                    "label": "گارانتی",
                    "input_type": "multi_select",
                    "options": guaranties
                },
                {
                    "name": "visible_in_site",
                    "label": "قابل نمایش",
                    "input_type": "checkbox",
                },
                {
                    "name": "approved",
                    "label": "تایید شده",
                    "input_type": "checkbox",
                },
                {
                    "name": "available",
                    "label": "موجود",
                    "input_type": "checkbox",
                },
                {
                    "name": "steps",
                    "label": "مرحله",
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
            warehouses = list(client.warehouses_collection.find({}, {"_id": 0}))
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
                     informal_price: dict,
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
            if special_from_date:
                update_data.update({
                    f"warehouse_details.{customer_type}.storages.{storage_id}.special_from_date": special_from_date
                })
            if special_to_date:
                update_data.update({
                    f"warehouse_details.{customer_type}.storages.{storage_id}.special_to_date": special_to_date
                })
            warehouses = list(client.warehouses_collection.find({}, {"_id": 0}))
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
                return "price updated successfully"
            return None


class Quantity:

    def __init__(self, system_code, customer_types):
        self.system_code = system_code
        self.customer_types = customer_types

    def set_quantity(self):
        with MongoConnection() as client:
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
    def get_stock(system_code: str) -> dict:
        """
        get physical stock of products
        """
        with MongoConnection() as client:
            db_stocks = list(client.stocks_collection.find({"systemCode": system_code}, {"_id": 0}))
            result = {
                "total": 0,
                "storages": []
            }
            for stock in db_stocks:
                quantity = stock["quantity"] - stock["reserve"]
                result["total"] += quantity
                wearhouses = client.warehouses_collection.find_one({"warehouse_id": int(stock["stockId"])}, {"_id": 0})
                result["storages"].append({"storage_id": stock["stockId"],
                                           "storage_label": wearhouses["warehouse_name"],
                                           "stock": quantity})
            return result

    @staticmethod
    def get_all_stocks():
        """
        get all stocks
        """
        with MongoConnection() as client:
            return list(client.warehouses_collection.find({"isActive": True}, {"_id": 0,
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
            storage = {
                "storage_id": storage_id,
                "reserved": 0,
                "quantity": quantity,
                "min_qty": min_qty,
                "max_qty": max_qty
            }
            warehouses = list(client.warehouses_collection.find({}, {"_id": 0}))
            obj = [i for i in warehouses if str(i['warehouse_id']) == storage['storage_id']]
            storage.update({"warehouse_state": obj[0].get("state"), "warehouse_city": obj[0].get("city"),
                            "warehouse_state_id": obj[0].get("state_id"),
                            "warehouse_city_id": obj[0].get("city_id"),
                            "warehouse_label": obj[0].get("warehouse_name"),
                            })
            db_query = {f"warehouse_details.{customer_type}.storages.{storage_id}.{key}": value for key, value in
                        storage.items()}

            db_query.update({
                "step": {"$cond": [{"$eq": ["$step", 3]}, 4, "$step"]}
            })

            result = client.product.update_one({"system_code": system_code}, [{"$set": db_query}])

            if result.modified_count:
                return 'quantity updated successfully'
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
                return {"message": "attribute added successfully", "label": "صفت با موفقیت اضافه شد"}, True
            return {"error": "attribute add failed", "label": "فرایند افزودن صفت به مشکل برخورد"}, False

# class Product(ABC):
#
#     @staticmethod
#     def get(system_code: str = None, page: int = 1, per_page: int = 10):
#         with MongoConnection() as mongo:
#             if not system_code:
#                 skips = per_page * (page - 1)
#                 re = '^[0-9]{9}$'
#                 data = mongo.collection.find({'system_code': {'$regex': re}}, {'_id': 0}).skip(skips).limit(per_page)
#                 counts = mongo.collection.count_documents({'system_code': {'$regex': re}})
#                 return {"page": page, "per_page": per_page, "total_counts": counts}, list(data)
#             re = '^' + system_code
#             result = mongo.collection.find({'system_code': {'$regex': re}}, {"_id": 0})
#             return list(result)
#
#     @staticmethod
#     def get_product_by_name(name, available_quantities, user_allowed_storages):
#         with MongoConnection() as mongo:
#             warehouses = list(mongo.warehouses_collection.find({}, {"_id": 0}))
#             storages_labels = list()
#             for allowed_storage in user_allowed_storages:
#                 obj = [i for i in warehouses if str(i['warehouse_id']) == allowed_storage]
#                 storages_labels.append({
#                     "storage_id": allowed_storage,
#                     "label": obj[0]['warehouse_name'] if obj else None
#                 })
#
#             result = mongo.collection.find(
#                 {"system_code": {"$in": list(available_quantities.keys())}, "visible_in_site": True,
#                  'name': re.compile(rf"^.*{name}.*$(?i)")
#                  },
#                 {"_id": 0})
#             product_list = list()
#             for product in result:
#                 if product.get("visible_in_site"):
#                     if product.get('products'):
#                         colors = [color.get('config', {}).get('color') for color in product['products'] if
#                                   color.get("visible_in_site")]
#                         product.update({"colors": colors})
#                         image = [child.get('attributes', {}).get('mainImage-pd') for child in product['products'] if
#                                  child.get('attributes', {}).get('mainImage-pd')]
#                         image = image[0] if image else None
#                         product.update({"image": image})
#                         del product['products']
#
#                         if colors:
#                             product_list.append(product)
#
#             return {"products": product_list, "storages": storages_labels}
#
#     @staticmethod
#     def get_product_by_system_code(system_code, lang):
#         """
#         """
#         with MongoConnection() as mongo:
#             result = mongo.collection.find_one({'system_code': system_code}, {"_id": 0})
#             if result and result.get("visible_in_site"):
#                 with RedisConnection() as redis_db:
#                     if result and result.get('products'):
#                         visible_products = list()
#                         for product in result['products']:
#                             if product.get("visible_in_site"):
#                                 for key, value in product['config'].items():
#                                     label = redis_db.client.hget(value, lang) if key != "images" else None
#                                     product['config'][key] = {
#                                         "value": value,
#                                         "attribute_label": redis_db.client.hget(key, lang),
#                                         "label": RamStorageTranslater(value,
#                                                                       lang).translate() if key == "storage" or key == "ram" else label
#                                     }
#                                     if key == "images":
#                                         del product['config'][key]['label']
#                                         del product['config'][key]['label']
#
#                                 attributes_data = list(mongo.attributes_collection.find(
#                                     {}, {
#                                         "_id": 0,
#                                         "name": 1,
#                                         "ecommerce_use_in_filter": 1,
#                                         "ecommerce_use_in_search": 1,
#                                         "editable_in_ecommerce": 1,
#                                         "editable_in_portal": 1,
#                                         "label": 1,
#                                         "portal_use_in_filter": 1,
#                                         "portal_use_in_search": 1,
#                                         "show_in_ecommerce": 1,
#                                         "show_in_portal": 1,
#                                     }
#                                 ))
#
#                                 attributes_list = list()
#
#                                 for key, value in product.get("attributes", {}).items():
#                                     stored_data = [attr for attr in attributes_data if attr['name'] == key][0]
#                                     stored_data['value'] = value
#                                     attributes_list.append(stored_data)
#
#                                 product['attributes'] = attributes_list
#
#                                 visible_products.append(product)
#
#                         result['products'] = visible_products
#                         kowsar_data = mongo.kowsar_collection.find_one({"system_code": system_code[:9]}, {"_id": 0})
#                         result.update({
#                             "routes": {
#                                 "route": result.get('main_category'),
#                                 "label": kowsar_data.get('main_category_label'),
#                                 "system_code": system_code[:2],
#                                 "child": {
#                                     "route": result.get('sub_category'),
#                                     "label": kowsar_data.get('sub_category_label'),
#                                     "system_code": system_code[:4],
#                                     "child": {
#                                         "route": result.get('brand'),
#                                         "label": kowsar_data.get('brand_label'),
#                                         "system_code": system_code[:6]
#                                     }
#                                 }
#                             }
#                         })
#                     return result
#             return None
#
#     @staticmethod
#     def get_product_list_by_system_code(system_code, page, per_page, available_quantities, allowed_storages):
#         with MongoConnection() as mongo:
#             def db_data_getter(query):
#                 result = mongo.kowsar_collection.find_one(query, {"_id": 0})
#                 return result if result else {}
#
#             warehouses = list(mongo.warehouses_collection.find({}, {"_id": 0}))
#             storages_labels = list()
#             for allowed_storage in allowed_storages:
#                 obj = [i for i in warehouses if str(i['warehouse_id']) == allowed_storage]
#                 storages_labels.append({
#                     "storage_id": allowed_storage,
#                     "label": obj[0]['warehouse_name'] if obj else None
#                 })
#
#             skips = per_page * (page - 1)
#             result_brand = mongo.collection.distinct("brand",
#                                                      {"system_code": {"$regex": f"^{str(system_code)[:2]}",
#                                                                       "$in": list(available_quantities.keys())
#                                                                       },
#                                                       "visible_in_site": True})
#             brands_list = list()
#             for brand in result_brand:
#                 brand_data = db_data_getter({"brand": brand, "system_code": {"$regex": "^.{6}$"}})
#                 brands_list.append({"name": brand, "label": brand_data.get("brand_label"),
#                                     "route": brand.replace(" ", ""),
#                                     "system_code": brand_data.get(
#                                         "system_code"),
#                                     })
#
#             system_code_list = [i for i in list(available_quantities.keys()) if i[:len(system_code)] == system_code]
#             result = mongo.collection.find(
#                 {"system_code": {"$in": system_code_list}, "visible_in_site": True},
#                 {"_id": 0}).skip(skips).limit(per_page)
#             products_count = mongo.collection.count_documents(
#                 {"system_code": {"$in": system_code_list}, "visible_in_site": True})
#
#             product_list = list()
#             for product in result:
#                 if product.get("visible_in_site"):
#                     if product.get('products'):
#                         colors = list({color.get('config', {}).get('color') for color in product['products'] if
#                                   color.get("visible_in_site")})
#                         product.update({"colors": colors})
#                         image = [child.get('attributes', {}).get('mainImage-pd') for child in product['products'] if
#                                  child.get('attributes', {}).get('mainImage-pd')]
#                         image = image[0] if image else None
#                         product.update({"image": image})
#                         del product['products']
#
#                         if colors:
#                             product_list.append(product)
#
#             return {"brands": brands_list, "products": product_list, "products_count": products_count,
#                     "storages_list": storages_labels}
#
#     @staticmethod
#     def get_category_list(available_quantities):
#         with MongoConnection() as mongo:
#             def db_data_getter(query):
#                 result = mongo.kowsar_collection.find_one(query, {"_id": 0})
#                 return result if result else {}
#
#             result_Accessory = mongo.collection.distinct("sub_category",
#                                                          {"main_category": "Accessory", "visible_in_site": True,
#                                                           "system_code": {"$in": list(available_quantities.keys())}
#                                                           })
#
#             category_list_Accessory = list()
#             for category in result_Accessory:
#                 kowsar_data = db_data_getter({"sub_category": category, "system_code": {"$regex": "^.{6}$"}})
#                 category_list_Accessory.append({"name": category, "label": kowsar_data.get("sub_category_label"),
#                                                 "route": category.replace(" ", ""),
#                                                 "system_code": kowsar_data.get("system_code"),
#                                                 "image": kowsar_data.get("image"),
#                                                 })
#
#             result_main_category = mongo.collection.distinct("main_category", {"visible_in_site": True,
#                                                                                "system_code": {"$in": list(
#                                                                                    available_quantities.keys())
#                                                                                }})
#             category_list_main_category = list()
#             for category in result_main_category:
#                 kowsar_data = db_data_getter({"main_category": category, "system_code": {"$regex": "^.{2}$"}})
#                 category_list_main_category.append(
#                     {"name": category, "label": kowsar_data.get("main_category_label"),
#                      "route": category.replace(" ", ""),
#                      "system_code": kowsar_data.get("system_code"),
#                      "image": kowsar_data.get("image")
#                      }
#                 )
#
#             result_brand = mongo.collection.distinct("brand", {"sub_category": "Mobile", "visible_in_site": True,
#                                                                "system_code": {"$in": list(available_quantities.keys())}
#                                                                })
#             category_list_brand = list()
#
#             for brand in result_brand:
#                 kowsar_data = db_data_getter({"brand": brand, "system_code": {"$regex": "^.{6}$"}})
#                 category_list_brand.append(
#                     {"name": brand, "label": kowsar_data.get("brand_label"),
#                      "route": brand.replace(" ", ""),
#                      "system_code": kowsar_data.get("system_code"),
#                      "image": kowsar_data.get("image")
#                      })
#
#             result_latest_product = list(mongo.collection.find(
#                 {"sub_category": "Mobile", "products": {"$ne": None}, "visible_in_site": True,
#                  "system_code": {"$in": list(available_quantities.keys())},
#                  "products.visible_in_site": True},
#                 {"_id": 0, "system_code": 1, "name": 1,
#                  "products": {
#                      "$elemMatch": {"visible_in_site": True},
#                  },
#                  "route": "$name"
#                  }).sort("products.date", -1).limit(20))
#
#             product_list = list()
#             for product in result_latest_product:
#                 product['route'] = product['route'].replace(" ", "")
#                 colors = [color['config']['color'] for color in product['products'] if
#                           color.get("visible_in_site")]
#                 product.update({"colors": colors})
#                 image = [child.get('attributes', {}).get('mainImage-pd') for child in product['products'] if
#                          child.get('attributes', {}).get('mainImage-pd')]
#                 image = image[0] if image else None
#                 product.update({"image": image})
#                 del product['products']
#
#                 product_list.append(product)
#
#             result_latest_product = product_list
#             return {
#                 "categories": {
#                     "label": "دسته بندی",
#                     "items": category_list_main_category},
#                 "mobile": {
#                     "label": "برند های موبایل",
#                     "items": category_list_brand},
#                 "accessory": {
#                     "label": "دسته بندی لوازم جانبی",
#                     "items": category_list_Accessory},
#                 "product": {
#                     "label": "جدیدترین محصولات",
#                     "items": result_latest_product
#                 }
#             }
#
#     @staticmethod
#     def get_product_attributes(system_code):
#         with MongoConnection() as mongo:
#             result = mongo.collection.find_one({"products.system_code": system_code}, {"_id": 0})
#             if result:
#                 out_data = {
#                     "name": result['name'],
#                     "system_code": result['system_code'],
#                     "brand": result['brand'],
#                     "mainCategory": result['main_category'],
#                     "model": result['model'],
#                     "subCategory": result['sub_category'],
#                 }
#
#                 db_attribute = mongo.attributes_collection.find({}, {"_id": 0})
#                 result_attribute = list()
#                 for obj in db_attribute:
#                     if obj.get("set_to_nodes"):
#                         len_parent = len(obj.get("parent")) if obj.get("parent") else 0
#                         if system_code[:len_parent] == obj.get("parent"):
#                             result_attribute.append(obj)
#                     else:
#                         if obj.get("parent") == system_code:
#                             result_attribute.append(obj)
#
#                 if result_attribute:
#                     out_data.update({
#                         "attributes": result_attribute
#                     })
#                     return out_data, True
#                 return "attribute not found", False
#             return "product not found", False
#
#     @staticmethod
#     def get_product_list_back_office(brands, sellers, colors, date,
#                                      guarantees, steps, visible_in_site, approved, available, page,
#                                      per_page, system_codes_list, lang):
#
#         with MongoConnection() as mongo, RedisConnection() as redis_db:
#             def db_data_getter(query):
#                 result = mongo.kowsar_collection.find_one(query, {"_id": 0})
#                 return result if result else {}
#
#             colors_list = [{"value": i, "label": redis_db.client.hget(i, lang)} for i in
#                            mongo.collection.distinct("products.config.color")]
#             brands_list = [{"value": i, "label": db_data_getter({"brand": i, "system_code": {"$regex": "^.{6}$"}}).get(
#                 "brand_label", i)} for i in
#                            mongo.collection.distinct("brand")]
#             warehouses_list = list()
#             seller_list = [{"value": i, "label": redis_db.client.hget(i, lang)} for i in
#                            mongo.collection.distinct("products.config.seller")]
#             guarantee_list = [{"value": i, "label": redis_db.client.hget(i, lang)} for i in
#                               mongo.collection.distinct("products.config.guarantee")]
#             step_list = mongo.collection.distinct("products.step")
#
#             skip = (page - 1) * per_page
#             limit = per_page
#
#             query = {
#                 "archived": {"$ne": True},
#             }
#             if brands:
#                 query["brand"] = {"$in": brands}
#             if sellers:
#                 query["products.config.seller"] = {"$in": sellers}
#             if colors:
#                 query["products.config.color"] = {"$in": colors}
#             if date:
#                 query["date"] = {}
#                 if date[0]:
#                     query["date"]["$gt"] = date[0]
#                 if date[1]:
#                     query["date"]["$lt"] = date[1]
#
#             if guarantees:
#                 query["products.config.guarantee"] = {"$in": guarantees}
#             if steps:
#                 query["products.step"] = {"$in": steps}
#             if visible_in_site:
#                 query["visible_in_site"] = visible_in_site
#             if approved:
#                 query["approved"] = approved
#             if system_codes_list:
#                 query["system_code"] = {"$in": system_codes_list}
#
#             query['products.$.archived'] = {'$ne': True}
#
#             len_db = len(list(mongo.collection.find(query, {"_id": 1})))
#             db_result = list(mongo.collection.find(query, {"_id": 0}).skip(skip).limit(limit))
#
#             product_list = list()
#             for parent in db_result:
#                 childs = list()
#                 for child in parent.get("products", []):
#                     if not child.get("archived"):
#                         for key, value in child['config'].items():
#                             label = redis_db.client.hget(value, lang) if key != "images" else None
#                             child['config'][key] = RamStorageTranslater(value,
#                                                                         lang).translate() if key == "storage" or key == "ram" else label
#
#                         childs.append(child)
#                 parent.update({"products": childs})
#                 product_list.append(parent)
#             filters = [
#                 {
#                     "name": "brands",
#                     "label": "برند",
#                     "input_type": "multi_select",
#                     "options": brands_list
#                 },
#                 {
#                     "name": "colors",
#                     "label": "رنگ",
#                     "input_type": "multi_select",
#                     "options": colors_list
#                 },
#                 {
#                     "name": "price",
#                     "label": "قیمت",
#                     "input_type": "range",
#                 },
#                 {
#                     "name": "warehouse",
#                     "label": "انبار",
#                     "input_type": "multi_select",
#                     "options": warehouses_list
#                 },
#                 {
#                     "name": "sellers",
#                     "label": "فروشنده",
#                     "input_type": "multi_select",
#                     "options": seller_list
#                 },
#                 {
#                     "name": "quantity",
#                     "label": "تعداد",
#                     "input_type": "range",
#                 },
#                 {
#                     "name": "date",
#                     "label": "تاریخ",
#                     "input_type": "date",
#                 },
#                 {
#                     "name": "guarantees",
#                     "label": "گارانتی",
#                     "input_type": "multi_select",
#                     "options": guarantee_list
#                 },
#                 {
#                     "name": "visible_in_site",
#                     "label": "قابل نمایش",
#                     "input_type": "checkbox",
#                 },
#                 {
#                     "name": "approved",
#                     "label": "تایید شده",
#                     "input_type": "checkbox",
#                 },
#                 {
#                     "name": "available",
#                     "label": "موجود",
#                     "input_type": "checkbox",
#                 },
#                 {
#                     "name": "steps",
#                     "label": "مرحله",
#                     "input_type": "multi_select",
#                     "options": step_list
#                 }
#             ]
#             return {
#                 "filters": filters,
#                 "result_len": len_db,
#                 "products": product_list
#             }
#
#     @staticmethod
#     def step_up_product(system_code):
#         with MongoConnection() as mongo:
#             mongo.collection.update_one({"products.system_code": system_code}, {"$inc": {"products.$.step": 1}})
#         return True
#
#     @staticmethod
#     def get_product_child(system_code, lang):
#         with MongoConnection() as mongo:
#             db_result = mongo.collection.find_one({"products.system_code": system_code}, {"_id": 0,
#                                                                                           "system_code": 1,
#                                                                                           "name": 1,
#                                                                                           "products": {"$elemMatch": {
#                                                                                               "system_code": system_code}}})
#             if db_result:
#                 name = db_result.get("name")
#                 parent_system_code = db_result.get("system_code")
#                 product = db_result.get("products")[0]
#                 with RedisConnection() as redis_db:
#                     for key, value in product['config'].items():
#                         label = redis_db.client.hget(value, lang) if key != "images" else None
#                         product['config'][key] = {
#                             "value": value,
#                             "attribute_label": redis_db.client.hget(key, lang),
#                             "label": RamStorageTranslater(value,
#                                                           lang).translate() if key == "storage" or key == "ram" else label
#                         }
#                         if key == "images":
#                             del product['config'][key]['label']
#                             del product['config'][key]['label']
#                 return {
#                     "name": name,
#                     "parent_system_code": parent_system_code,
#                     "product": product
#                 }
#
#             return None
#
#     @abstractmethod
#     def system_code_is_unique(self) -> bool:
#         """
#         something
#         """
#         pass
#
#     @abstractmethod
#     def create(self) -> tuple:
#         """
#         something
#         """
#         pass
#
#     @abstractmethod
#     def delete(self) -> tuple:
#         """
#         something
#         """
#         pass


# class CreateParent(Product):
#
#     def __init__(self, system_code, name, url_name):
#         self.system_code = system_code
#         self.name = name
#         self.url_name = url_name
#         self.main_category = None
#         self.sub_category = None
#         self.brand = None
#         self.model = None
#         self.attributes = None
#         self.jalali_date = jalali_now()
#         self.date = gregorian_now()
#
#     @staticmethod
#     def get_configs(system_code):
#         with MongoConnection() as mongo:
#             parents = list(mongo.parent_col.find({"system_code": {"$regex": f"^{system_code}"}}, {"_id": 0}))
#             stored_parents = mongo.collection.distinct("system_code", {"system_code": {"$regex": f"^{system_code}"}})
#             for parent in parents:
#                 if parent['system_code'] in stored_parents:
#                     parent.update({
#                         "created": True
#                     })
#             return parents
#
#     def system_code_is_unique(self) -> bool:
#         with MongoConnection() as mongo:
#             result = mongo.collection.find_one({'system_code': self.system_code})
#             return False if result else True
#
#     def set_kowsar_data(self, data: dict) -> None:
#         self.main_category = data.get('main_category')
#         self.sub_category = data.get('sub_category')
#         self.brand = data.get('brand')
#         self.model = data.get('model')
#         self.attributes = data.get('attributes')
#
#     def create(self) -> tuple:
#         """
#         Adds a product to main collection in database.
#         The system_code of the product should be unique!
#         """
#         with MongoConnection() as mongo:
#             kowsar_data = mongo.parent_col.find_one({'system_code': self.system_code}, {'_id': 0})
#             if not kowsar_data:
#                 return {"error": "product not found in kowsar", "label": "محصول در کوثر یافت نشد"}, False
#             self.set_kowsar_data(kowsar_data)
#             result = mongo.collection.insert_one(self.__dict__)
#         if result.inserted_id:
#             return {"message": "product created successfully", "label": "محصول با موفقیت ساخته شد"}, True
#         return {"error": "product creation failed", "label": "فرایند ساخت محصول به مشکل خورد"}, False
#
#     def delete(self) -> tuple:
#         with MongoConnection() as mongo:
#             result = mongo.collection.update_one({"system_code": self.system_code},
#                                                  {"$set": {"archived": True,
#                                                            "visible_in_site": False,
#                                                            }})
#             if result.modified_count:
#                 return {"message": "product archived successfully", "label": "محصول با موفقیت حذف شد"}, True
#             return {"message": "product failed to archive", "label": "حذف محصول با خطا مواجه شد"}, False
#
#     @staticmethod
#     def edit_product(system_code, data):
#         with MongoConnection() as mongo:
#             visible_in_site = data.get("visible_in_site")
#             result = mongo.collection.update_one({"system_code": system_code, "products.step": 5},
#                                                  {"$set": {"visible_in_site": visible_in_site}})
#             if result.modified_count:
#                 return {"message": "product visibility updated successfully",
#                         "label": "وضعیت نمایش محصول با موفقیت بروزرسانی شد"}
#             return {"message": "product visibility update failed",
#                     "label": "بروزرسانی وضعیت نمایش محصول با خطا مواجه شد"}
#
#
# class CreateChild(Product):
#
#     def __init__(self, system_code, parent_system_code):
#         self.system_code = system_code
#         self.parent_system_code = parent_system_code
#         self.step = 2
#         self.config = None
#         self.jalali_date = jalali_now()
#         self.date = gregorian_now()
#
#     def set_kowsar_data(self, data: dict) -> None:
#         self.config = data.get('config')
#
#     def system_code_is_unique(self) -> bool:
#         with MongoConnection() as mongo:
#             result = mongo.collection.find_one({'products.system_code': self.system_code})
#             return False if result else True
#
#     @staticmethod
#     def get_configs(system_code):
#         with MongoConnection() as mongo:
#             return list(mongo.collection.find({"system_code": {"$regex": f"^{system_code}"}}, {"_id": 0}))
#
#     def create(self) -> tuple:
#         """
#         Adds a product to main collection in database.
#         The system_code of the product should be unique!
#         """
#         with MongoConnection() as mongo:
#             kowsar_data = mongo.kowsar_collection.find_one({'system_code': self.system_code}, {'_id': 0})
#             if not kowsar_data:
#                 return {"error": "product not found in kowsar", "label": "محصول در کوثر یافت نشد"}, False
#             self.set_kowsar_data(kowsar_data)
#             product = self.__dict__
#             parent_system_code = self.parent_system_code
#             product.pop("parent_system_code")
#             result = mongo.collection.update_one(
#                 {"system_code": parent_system_code},
#                 {'$addToSet': {'products': product}})
#         if result.modified_count:
#             return {"message": f"product {self.system_code} created successfully",
#                     "label": f"محصول {self.system_code} با موفقیت ساخته شد"}, True
#         return {"error": f"product creation {self.system_code} failed",
#                 "label": f"فرایند ساخت محصول {self.system_code} به مشکل خورد"}, False
#
#     @staticmethod
#     def suggester(data, system_code, config):
#         with MongoConnection() as mongo:
#             with RedisConnection() as redis_db:
#                 sugested_products = list()
#                 system_codes = mongo.collection.distinct("products.system_code", {"system_code": system_code})
#                 for obj in data:
#                     if obj['system_code'] in system_codes:
#                         obj['created'] = True
#                         db_data = mongo.collection.find_one({"products.system_code": obj['system_code']},
#                                                             {"_id": 0, "products": {
#                                                                 "$elemMatch": {"system_code": obj['system_code']}}})
#                         obj['visibleInSite'] = db_data.get("products", [])[0].get("visible_in_site",
#                                                                                   False) if db_data else False
#                     if obj.get('label').get('storage') == config[0] and obj.get('label').get('ram') == config[1]:
#                         configs = obj.get('label')
#                         del obj['label']
#                         for key, value in configs.items():
#                             configs[key] = {
#                                 "value": value,
#                                 "attribute_label": redis_db.client.hget(key, "fa_ir"),
#                                 "label": redis_db.client.hget(value, "fa_ir") if key != 'storage' and key != 'ram'
#                                 else RamStorageTranslater(value, "fa_ir").translate()
#                             }
#                         obj['configs'] = configs
#                         sugested_products.append(obj)
#             return sugested_products
#
#     def delete(self) -> tuple:
#         with MongoConnection() as mongo:
#             result = mongo.collection.update_one({"products.system_code": self.system_code},
#                                                  {"$set": {"products.$.archived": True,
#                                                            "products.$.visible_in_site": False}})
#             if result.modified_count:
#                 return {"message": "product archived successfully", "label": "محصول با موفقیت حذف شد"}, True
#             return {"message": "product failed to archive", "label": "حذف محصول با خطا مواجه شد"}, False
#
#     @staticmethod
#     def edit_product(system_code, data):
#         with MongoConnection() as mongo:
#             visible_in_site = data.get("visible_in_site")
#             result = mongo.collection.update_one({"products.system_code": system_code, "products.step": 5},
#                                                  {"$set": {"products.$.visible_in_site": visible_in_site}})
#             if result.modified_count:
#                 return True
#             return False
