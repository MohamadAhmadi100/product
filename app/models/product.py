import re
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
    def system_code_exists(system_code):
        with MongoConnection() as mongo:
            result = mongo.product.find_one({"system_code": system_code})
            return True if result else False

    @staticmethod
    def price_list_bot(customer_type, system_code, initial):
        with MongoConnection() as mongo:
            pipe_lines = [{
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
                    'min_qty': "$zz.v.min_qty",
                    'max_qty': {
                        '$cond': [
                            {
                                '$gt': [
                                    '$zz.v.quantity', '$zz.v.max_qty'
                                ]
                            }, '$zz.v.max_qty', '$zz.v.quantity'
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
                }, {
                    '$addFields': {
                        'brand': {
                            'value': '$brand',
                            'label': '$brand'
                        },
                        'color': {
                            'value': '$color',
                            'label': '$color'
                        },
                        'guaranty': {
                            'value': '$guaranty',
                            'label': '$guaranty'
                        },
                        'main_category': {
                            'value': '$main_category',
                            'label': '$main_category'
                        },
                        'seller': {
                            'value': '$seller',
                            'label': '$seller'
                        },
                        'sub_category': {
                            'value': '$sub_category',
                            'label': '$sub_category'
                        }
                    }}
            ]
            result = list(mongo.product.aggregate(pipe_lines))
            if result:
                return result
            return None

    @staticmethod
    def price_list_all(customer_type, sub_category, brand, model, allowed_storages):
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
                                        '$zz.v.quantity', '$zz.v.max_qty'
                                    ]
                                }, '$zz.v.max_qty', '$zz.v.quantity'
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
                                        '$zz.v.quantity', '$zz.v.max_qty'
                                    ]
                                }, '$zz.v.max_qty', '$zz.v.quantity'
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
                        'storage_id': {
                            '$in': allowed_storages
                        }
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
                        'min_qty': "$zz.v.min_qty",
                        'max_qty': {
                            '$cond': [
                                {
                                    '$gt': [
                                        '$zz.v.quantity', '$zz.v.max_qty'
                                    ]
                                }, '$zz.v.max_qty', '$zz.v.quantity'
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
                            "brand": 1,
                            'main_category': 1,
                            'model': 1,
                            'sub_category': 1,
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
                                            "label": redis.client.hget(product['color'], lang),
                                            "hex": redis.client.hget(product['color'], "hex")
                                            }
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
            warehouses_list = list(mongo.warehouses.find({"isActive": True}, {"_id": 0,
                                                                              "storage_id": {
                                                                                  "$convert": {"input": "$warehouse_id",
                                                                                               "to": "string"}},
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
                return "price updated successfully"
            return None


class Quantity:

    def __init__(self, system_code, customer_types):
        self.system_code = system_code
        self.customer_types = customer_types

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
                wearhouses = client.warehouses.find_one({"warehouse_id": int(stock["stockId"])}, {"_id": 0})
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
