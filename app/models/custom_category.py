import jdatetime

from app.helpers.mongo_connection import MongoConnection


class KowsarCategories:
    def __init__(self, system_code, custom_name, visible_in_site, image):
        self.system_code = system_code
        self.custom_name = custom_name
        self.visible_in_site = visible_in_site
        self.image = image

    def create(self, category_label):
        """
        Do Database Insertion
        """
        with MongoConnection() as mongo:
            result = mongo.kowsar_collection.update_many({'system_code': {"$regex": "^" + self.system_code}},
                                                         {'$set': {category_label: self.custom_name
                                                                   }})
            visible_result = mongo.kowsar_collection.update_one({'system_code': self.system_code},
                                                                {'$set': {'visible_in_site': self.visible_in_site,
                                                                          'image': self.image
                                                                          }})
            if result.modified_count > 0 or visible_result.modified_count > 0:
                return True
            elif result.matched_count > 0 and visible_result.matched_count > 0:
                return "Category already exists"
            return None

    @staticmethod
    def get_all_categories():
        with MongoConnection() as mongo:
            result = mongo.product.aggregate([
                {
                    '$project': {
                        'item': {
                            'main_category': '$main_category',
                            'sub_category': '$sub_category',
                            'system_code': {
                                '$substr': [
                                    '$system_code', 0, 9
                                ]
                            },
                            'brand': '$brand'
                        }
                    }
                }, {
                    '$group': {
                        '_id': None,
                        'item': {
                            '$addToSet': '$item'
                        }
                    }
                }
            ])
            result = result.next().get("item") if result.alive else []

            tree_data = []
            for obj in result:
                kowsar_data = list(mongo.kowsar_collection.find({"system_code": {"$in": [obj.get("system_code")[:2],
                                                                                         obj.get("system_code")[:6],
                                                                                         obj.get("system_code")[:9],
                                                                                         ]}}, {"_id": 0}).sort(
                    "system_code", 1))
                stored_main = next((x for x in tree_data if x['name'] == obj.get("main_category")), None)
                if stored_main:
                    index_main = tree_data.index(stored_main)
                    stored_sub = next(
                        (x for x in tree_data[index_main]['children'] if x['name'] == obj.get("sub_category"))
                        , None)
                    if stored_sub:
                        index_sub = tree_data[index_main]['children'].index(stored_sub)
                        if next((x for x in tree_data[index_main]['children'][index_sub]['children'] if
                                 x['name'] == obj.get("brand")), None):
                            continue
                        tree_data[index_main]['children'][index_sub]['children'].append(
                            {
                                'name': obj.get("brand"),
                                'title': kowsar_data[2].get("brand_label", obj.get("brand")),
                                'image': kowsar_data[2].get("image", None),
                                'visible_in_site': kowsar_data[2].get("visible_in_site", True),
                                "system_code": obj.get("system_code")[:9]
                            }
                        )
                        continue
                    tree_data[index_main]['children'].append(
                        {
                            'name': obj.get("sub_category"),
                            'title': kowsar_data[1].get("sub_category_label", obj.get("sub_category")),
                            'image': kowsar_data[1].get("image", None),
                            'visible_in_site': kowsar_data[1].get("visible_in_site", True),
                            "system_code": obj.get("system_code")[:6],
                            'children': [
                                {
                                    'name': obj.get("brand"),
                                    'title': kowsar_data[2].get("brand_label", obj.get("brand")),
                                    'image': kowsar_data[2].get("image", None),
                                    'visible_in_site': kowsar_data[2].get("visible_in_site", True),
                                    "system_code": obj.get("system_code")[:9]
                                }
                            ]
                        }
                    )
                    continue
                tree_data.append({
                    'name': obj.get("main_category"),
                    'title': kowsar_data[0].get("main_category_label", obj.get("main_category")),
                    'image': kowsar_data[0].get("image", None),
                    'visible_in_site': kowsar_data[0].get("visible_in_site", True),
                    "system_code": obj.get("system_code")[:2],
                    "children": [
                        {
                            'name': obj.get("sub_category"),
                            'title': kowsar_data[1].get("sub_category_label", obj.get("sub_category")),
                            'image': kowsar_data[1].get("image", None),
                            'visible_in_site': kowsar_data[1].get("visible_in_site", True),
                            "system_code": obj.get("system_code")[:6],
                            "children": [
                                {
                                    'name': obj.get("brand"),
                                    'title': kowsar_data[2].get("brand_label", obj.get("brand")),
                                    'image': kowsar_data[2].get("image", None),
                                    'visible_in_site': kowsar_data[2].get("visible_in_site", True),
                                    "system_code": obj.get("system_code")[:9]
                                }
                            ]
                        }
                    ]
                })

            return tree_data

    @staticmethod
    def get_products_by_category(system_code, page, per_page):
        with MongoConnection() as mongo:
            pipe_line = [
                {
                    '$match': {
                        'system_code': {"$regex": f"^{system_code}"}
                    },
                },
                {"$project": {
                    "_id": 0
                }
                },
                {
                    '$facet': {
                        'count': [
                            {
                                '$count': 'count'
                            }
                        ],
                        'data': [
                            {
                                '$skip': (page - 1) * per_page
                            }, {
                                '$limit': per_page
                            }
                        ]
                    }
                }
            ]
            result = mongo.product.aggregate(pipe_line)
            result = result.next() if result.alive else {}
            return {"count": result.get("count")[0].get("count", 0), "data": result.get("data")}


class CustomCategories:
    def __init__(self, name, products, visible_in_site, image):
        self.name = name
        self.products = products
        self.visible_in_site = visible_in_site
        self.image = image
        self.created_at = jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def is_unique(self):
        """
        Check if category already exists
        """
        with MongoConnection() as mongo:
            result = mongo.custom_category.find_one({'name': self.name})
            if result:
                return False
            return True

    def create(self):
        """
        Do Database Insertion
        """
        with MongoConnection() as mongo:
            result = mongo.custom_category.insert_one(self.__dict__)
            if result.inserted_id:
                return True
            return None

    @staticmethod
    def get(visible_in_site, page, per_page, created_at_from, created_at_to):
        """
        get all products by system code from custom category database
        """
        skip = (page - 1) * per_page
        limit = per_page

        query = {}
        if visible_in_site is not None:
            query["visible_in_site"] = visible_in_site

        if created_at_from or created_at_to:
            query["created_at"] = {}
            if created_at_to:
                query["created_at"]["$lte"] = created_at_to
            if created_at_from:
                query["created_at"]["$gte"] = created_at_from

        with MongoConnection() as mongo:
            len_db = mongo.custom_category.count_documents(query)
            db_result = list(mongo.custom_category.find(query, {"_id": 0}).skip(skip).limit(limit))
            if len_db > 0:
                for category in db_result:
                    category['products'] = list(mongo.product.find({"system_code": {"$in": category['products']}},
                                                                   {"_id": 0}))

            return {
                "total": len_db,
                "data": db_result
            }

    @staticmethod
    def delete(name):
        """
        Delete custom category by name
        """
        with MongoConnection() as mongo:
            result = mongo.custom_category.delete_one({"name": name})
            if result.deleted_count:
                return True
            return None

    @staticmethod
    def edit(name, new_name, products, visible_in_site, image):
        """
        Edit custom category by name
        """
        set_dict = {}
        if new_name:
            set_dict["name"] = new_name
        if products:
            set_dict["products"] = products
        if visible_in_site is not None:
            set_dict["visible_in_site"] = visible_in_site
        if image:
            set_dict["image"] = image
        with MongoConnection() as mongo:
            result = mongo.custom_category.update_one({"name": name}, {
                "$set": set_dict
            })
            if result.matched_count:
                if result.modified_count:
                    return True, "???????????? ???? ???????????? ?????????? ????"
                return None, "???????????? ???? ???????? ?????????? ????"
            return None, "???????? ???????? ???????? ?????? ???????? ??????"
