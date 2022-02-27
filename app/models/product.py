from abc import ABC, abstractmethod

from app.helpers.date_convertor import jalali_now, gregorian_now
from app.helpers.mongo_connection import MongoConnection
from app.helpers.redis_connection import RedisConnection
from app.modules.translator import RamStorageTranslater


# from app.validators.attribute_validator import attribute_validator


class Product(ABC):

    @staticmethod
    def get_all_categories(system_code, page, per_page):
        with MongoConnection() as mongo:
            if system_code == "00":
                items = list(mongo.collection.find({}, {"system_code": {"$substr": ["$system_code", 0, 2]}, "_id": 0,
                                                        "label": "$main_category"}))
            elif len(system_code) == 2:
                items = mongo.collection.find({"system_code": {"$regex": f"^{system_code}"}},
                                              {"system_code": {"$substr": ["$system_code", 0, 4]}, "_id": 0,
                                               "label": "$sub_category"})
            elif len(system_code) == 4:
                items = mongo.collection.find({"system_code": {"$regex": f"^{system_code}"}},
                                              {"system_code": {"$substr": ["$system_code", 0, 6]}, "_id": 0,
                                               "label": "$brand"})
            elif len(system_code) == 6:
                skip = (page - 1) * per_page
                items = mongo.collection.find({"system_code": {"$regex": f"^{system_code}"}},
                                              {"system_code": {"$substr": ["$system_code", 0, 9]}, "_id": 0,
                                               "label": "$model"}).skip(skip).limit(per_page)
            return [dict(t) for t in {tuple(d.items()) for d in items}]

    @staticmethod
    def get(system_code: str = None, page: int = 1, per_page: int = 10):
        with MongoConnection() as mongo:
            if not system_code:
                skips = per_page * (page - 1)
                re = '^[0-9]{9}$'
                data = mongo.collection.find({'system_code': {'$regex': re}}, {'_id': 0}).skip(skips).limit(per_page)
                counts = mongo.collection.count_documents({'system_code': {'$regex': re}})
                return {"page": page, "per_page": per_page, "total_counts": counts}, list(data)
            re = '^' + system_code
            result = mongo.collection.find({'system_code': {'$regex': re}}, {"_id": 0})
            return list(result)

    @staticmethod
    def get_product_by_system_code(system_code, lang):
        """
        """
        with MongoConnection() as mongo:
            result = mongo.collection.find_one({'system_code': system_code}, {"_id": 0})
            if result and result.get("visible_in_site"):
                with RedisConnection() as redis_db:
                    if result and result.get('products'):
                        for product in result['products']:
                            if product.get("visible_in_site"):
                                for key, value in product['config'].items():
                                    label = redis_db.client.hget(value, lang) if key != "images" else None
                                    product['config'][key] = {
                                        "value": value,
                                        "attribute_label": redis_db.client.hget(key, lang),
                                        "label": RamStorageTranslater(value,
                                                                      lang).translate() if key == "storage" or key == "ram" else label
                                    }
                                    if key == "images":
                                        del product['config'][key]['label']
                                        del product['config'][key]['label']
                            else:
                                result['products'].remove(product)
                        result.update({
                            "routes": {
                                "route": result.get('main_category'),
                                "label": redis_db.client.hget(result.get('main_category'), lang),
                                "child": {
                                    "route": result.get('sub_category'),
                                    "label": redis_db.client.hget(result.get('sub_category'), lang),
                                    "child": {
                                        "route": result.get('brand'),
                                        "label": redis_db.client.hget(result.get('brand'), lang),
                                    }
                                }
                            }
                        })
                    return result
            return None

    @staticmethod
    def get_product_list(brand, page, per_page):
        with MongoConnection() as mongo:
            with RedisConnection() as redis_db:
                skips = per_page * (page - 1)
                db_brands = mongo.collection.distinct("brand")
                brands_dict = [{"brand": brands, "label": redis_db.client.hget(brands, "fa_ir"),
                                "active": True if brands == brand else False} for brands in db_brands]
                result = mongo.collection.find({"brand": brand}, {"_id": 0}).skip(skips).limit(per_page)
                product_list = list()
                for product in result:
                    if product.get("visible_in_site"):
                        if product.get('products'):
                            colors = [color['config']['color'] for color in product['products'] if
                                      color.get("visible_in_site")]
                            product.update({"colors": colors})
                            del product['products']
                            product_list.append(product)

                return {"brands": brands_dict, "products": product_list}

    @staticmethod
    def get_category_list():
        with MongoConnection() as mongo:
            with RedisConnection() as redis_db:
                result_Accessory = mongo.collection.distinct("sub_category", {"main_category": "Accessory"})
                category_list_Accessory = [{"sub_category": category, "label": redis_db.client.hget(category, "fa_ir")}
                                           for category in result_Accessory]

                result_main_category = mongo.collection.distinct("main_category")
                category_list_main_category = [
                    {"main_category": category, "label": redis_db.client.hget(category, "fa_ir")}
                    for category in result_main_category]

                result_brand = mongo.collection.distinct("brand", {"sub_category": "Mobile"})
                category_list_brand = [{"brand": brand, "label": redis_db.client.hget(brand, "fa_ir")}
                                       for brand in result_brand]

                result_latest_product = mongo.collection.find(
                    {"sub_category": "Mobile", "products": {"$ne": None}, "visible_in_site": True,
                     "products.visible_in_site": True},

                    {"_id": 0, "system_code": 1, "name": 1,
                     "products": {"$elemMatch": {"visible_in_site": True}},
                     }).sort("date", -1).limit(20)
                return {
                    "category_list_Accessory": category_list_Accessory,
                    "category_list_main_category": category_list_main_category,
                    "category_list_brand": category_list_brand,
                    "latest_product": list(result_latest_product)
                }

    @staticmethod
    def get_product_list_back_office():
        colors_list = list()
        brands_list = list()
        warehouses_list = list()
        seller_list = list()
        gaurantee_list = list()
        step_list = list()
        return {
            "filters": [
                {
                    "name": "brand",
                    "label": "برند",
                    "input_type": "multi_select",
                    "options": brands_list
                },
                {
                    "name": "color",
                    "label": "رنگ",
                    "input_type": "multi_select",
                    "options": colors_list
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
                    "name": "seller",
                    "label": "فروشنده",
                    "input_type": "multi_select",
                    "options": seller_list
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
                    "name": "gaurantee",
                    "label": "گارانتی",
                    "input_type": "multi_select",
                    "options": gaurantee_list
                },
                {
                    "name": "visibleInSite",
                    "label": "قابل نمایش",
                    "input_type": "checkbox",
                },
                {
                    "name": "aproved",
                    "label": "تایید شده",
                    "input_type": "checkbox",
                },
                {
                    "name": "available",
                    "label": "موجود",
                    "input_type": "checkbox",
                },
                {
                    "name": "step",
                    "label": "مرحله",
                    "input_type": "multi_select",
                    "options": step_list
                }
            ]
        }

    @abstractmethod
    def system_code_is_unique(self) -> bool:
        """
        something
        """
        pass

    @abstractmethod
    def create(self) -> tuple:
        """
        something
        """
        pass

    @abstractmethod
    def delete(self) -> tuple:
        """
        something
        """
        pass


class CreateParent(Product):

    def __init__(self, system_code, name, visible_in_site):
        self.system_code = system_code
        self.name = name
        self.visible_in_site = visible_in_site
        self.main_category = None
        self.sub_category = None
        self.brand = None
        self.model = None
        self.attributes = None
        self.jalali_date = jalali_now()
        self.date = gregorian_now()

    @staticmethod
    def get_configs(system_code):
        with MongoConnection() as mongo:
            parents = list(mongo.parent_col.find({"system_code": {"$regex": f"^{system_code}"}}, {"_id": 0}))
            stored_parents = mongo.collection.distinct("system_code", {"system_code": {"$regex": f"^{system_code}"}})
            for parent in parents:
                if parent['system_code'] in stored_parents:
                    parent.update({
                        "created": True
                    })
            return parents

    def system_code_is_unique(self) -> bool:
        with MongoConnection() as mongo:
            result = mongo.collection.find_one({'system_code': self.system_code})
            return False if result else True

    def set_kowsar_data(self, data: dict) -> None:
        self.main_category = data.get('main_category')
        self.sub_category = data.get('sub_category')
        self.brand = data.get('brand')
        self.model = data.get('model')
        self.attributes = data.get('attributes')

    def create(self) -> tuple:
        """
        Adds a product to main collection in database.
        The system_code of the product should be unique!
        """
        with MongoConnection() as mongo:
            kowsar_data = mongo.parent_col.find_one({'system_code': self.system_code}, {'_id': 0})
            if not kowsar_data:
                return {"error": "product not found in kowsar", "label": "محصول در کوثر یافت نشد"}, False
            self.set_kowsar_data(kowsar_data)
            result = mongo.collection.insert_one(self.__dict__)
        if result.inserted_id:
            return {"message": "product created successfully", "label": "محصول با موفقیت ساخته شد"}, True
        return {"error": "product creation failed", "label": "فرایند ساخت محصول به مشکل خورد"}, False

    def delete(self) -> tuple:
        pass


class CreateChild(Product):

    def __init__(self, system_code, parent_system_code, visible_in_site):
        self.system_code = system_code
        self.parent_system_code = parent_system_code
        self.visible_in_site = visible_in_site
        self.step = 2
        self.config = None
        self.jalali_date = jalali_now()
        self.date = gregorian_now()

    def set_kowsar_data(self, data: dict) -> None:
        self.config = data.get('config')

    def system_code_is_unique(self) -> bool:
        with MongoConnection() as mongo:
            result = mongo.collection.find_one({'products.system_code': self.system_code})
            return False if result else True

    @staticmethod
    def get_configs(system_code):
        with MongoConnection() as mongo:
            return list(mongo.collection.find({"system_code": {"$regex": f"^{system_code}"}}, {"_id": 0}))

    def create(self) -> tuple:
        """
        Adds a product to main collection in database.
        The system_code of the product should be unique!
        """
        with MongoConnection() as mongo:
            kowsar_data = mongo.kowsar_collection.find_one({'system_code': self.system_code}, {'_id': 0})
            if not kowsar_data:
                return {"error": "product not found in kowsar", "label": "محصول در کوثر یافت نشد"}, False
            self.set_kowsar_data(kowsar_data)
            product = self.__dict__
            parent_system_code = self.parent_system_code
            product.pop("parent_system_code")
            result = mongo.collection.update_one(
                {"system_code": parent_system_code},
                {'$addToSet': {'products': product}})
        if result.modified_count:
            return {"message": f"product {self.system_code} created successfully",
                    "label": f"محصول {self.system_code} با موفقیت ساخته شد"}, True
        return {"error": f"product creation {self.system_code} failed",
                "label": f"فرایند ساخت محصول {self.system_code} به مشکل خورد"}, False

    @staticmethod
    def suggester(data, system_code, config):
        with MongoConnection() as mongo:
            with RedisConnection() as redis_db:
                sugested_products = list()
                system_codes = mongo.collection.distinct("products.system_code", {"system_code": system_code})
                for obj in data:
                    if obj['system_code'] in system_codes:
                        obj['created'] = True
                    if obj.get('label').get('storage') == config[0] and obj.get('label').get('ram') == config[1]:
                        configs = obj.get('label')
                        del obj['label']
                        for key, value in configs.items():
                            configs[key] = {
                                "value": value,
                                "attribute_label": redis_db.client.hget(key, "fa_ir"),
                                "label": redis_db.client.hget(value, "fa_ir") if key != 'storage' and key != 'ram'
                                else RamStorageTranslater(value, "fa_ir").translate()
                            }
                        obj['configs'] = configs
                        sugested_products.append(obj)
            return sugested_products

    def delete(self) -> tuple:
        with MongoConnection() as mongo:
            result = mongo.collection.update_one({"products.system_code": self.system_code},
                                                 {"$set": {"products.$.archived": True}})
            if result.modified_count:
                return {"message": "product archived successfully", "label": "محصول با موفقیت حذف شد"}, True
            return {"message": "product failed to archive", "label": "حذف محصول با خطا مواجه شد"}, False


class AddAtributes(Product):

    def __init__(self, system_code, attributes):
        self.system_code = system_code
        self.attributes = attributes

    def system_code_is_unique(self) -> bool:
        with MongoConnection() as mongo:
            result = mongo.collection.find_one({'products.system_code': self.system_code})
            return False if result else True

    def create(self) -> tuple:
        with MongoConnection() as mongo:
            result = mongo.collection.update_one({"products.system_code": self.system_code},
                                                 {"$set": {"products.$.attributes": self.attributes, "products.$.step": 3}})
            if result.modified_count:
                return {"message": "attribute added successfully", "label": "صفت با موفقیت اضافه شد"}, True
            return {"error": "attribute add failed", "label": "فرایند افزودن صفت به مشکل برخورد"}, False

    def delete(self) -> tuple:
        pass
