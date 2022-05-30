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
    def get(system_code, page, per_page):
        """
        get all products by system code
        """
        skip = (page - 1) * per_page
        limit = per_page
        with MongoConnection() as mongo:
            len_db = len(list(mongo.collection.find({"archived": {"$ne": True},
                                                     "visible_in_site": True,
                                                     "products.visible_in_site": True,
                                                     "products.archived": {"$ne": True},
                                                     "system_code": {"$regex": "^" + system_code}
                                                     }, {"_id": 1})))
            db_result = list(mongo.collection.find({"archived": {"$ne": True},
                                                    "products.archived": {"$ne": True},
                                                    "visible_in_site": True,
                                                    "products.visible_in_site": True,
                                                    "system_code": {"$regex": "^" + system_code}
                                                    }, {"_id": 0}).skip(skip).limit(limit))

            product_list = list()
            for parent in db_result:
                childs = list()
                for child in parent.get("products", []):
                    if not child.get("archived") and child.get("visible_in_site"):
                        childs.append(child)
                parent.update({"products": childs})
                product_list.append(parent)

            return {
                "total": len_db,
                "data": product_list
            }

    @staticmethod
    def get_all_categories():
        with MongoConnection() as mongo:
            result = mongo.collection.find({}, {"_id": 0, "main_category": 1, "sub_category": 1, "system_code": 1,
                                                "brand": 1})

            tree_data = []
            for obj in result:
                kowsar_data = list(mongo.kowsar_collection.find({"system_code": {"$in": [obj.get("system_code")[:2],
                                                                                         obj.get("system_code")[:4],
                                                                                         obj.get("system_code")[:6],
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
                                "system_code": obj.get("system_code")[:6]
                            }
                        )
                        continue
                    tree_data[index_main]['children'].append(
                        {
                            'name': obj.get("sub_category"),
                            'title': kowsar_data[1].get("sub_category_label", obj.get("sub_category")),
                            'image': kowsar_data[1].get("image", None),
                            'visible_in_site': kowsar_data[1].get("visible_in_site", True),
                            "system_code": obj.get("system_code")[:4],
                            'children': [
                                {
                                    'name': obj.get("brand"),
                                    'title': kowsar_data[2].get("brand_label", obj.get("brand")),
                                    'image': kowsar_data[2].get("image", None),
                                    'visible_in_site': kowsar_data[2].get("visible_in_site", True),
                                    "system_code": obj.get("system_code")[:6]
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
                            "system_code": obj.get("system_code")[:4],
                            "children": [
                                {
                                    'name': obj.get("brand"),
                                    'title': kowsar_data[2].get("brand_label", obj.get("brand")),
                                    'image': kowsar_data[2].get("image", None),
                                    'visible_in_site': kowsar_data[2].get("visible_in_site", True),
                                    "system_code": obj.get("system_code")[:6]
                                }
                            ]
                        }
                    ]
                })

            return tree_data


class CustomCategories:
    def __init__(self, name, products, label, visible_in_site, image):
        self.name = name
        self.products = products
        self.label = label
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

        if created_at_from:
            query["created_at"] = {"$gte": created_at_from}
        if created_at_to:
            if query.get("created_at"):
                query["created_at"]["$lte"] = created_at_to
            else:
                query["created_at"] = {"$lte": created_at_to}

        with MongoConnection() as mongo:
            len_db = len(list(mongo.custom_category.find(query, {"_id": 1})))
            db_result = list(mongo.custom_category.find(query, {"_id": 0}).skip(skip).limit(limit))

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