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
                        visible_products = list()
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

                                visible_products.append(product)

                        result['products'] = visible_products
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
    def get_product_list_by_system_code(system_code, page, per_page):
        with MongoConnection() as mongo:
            def db_data_getter(query):
                result = mongo.kowsar_collection.find_one(query, {"_id": 0})
                return result if result else {}

            with RedisConnection() as redis_db:
                skips = per_page * (page - 1)
                is_brand = False
                if len(str(system_code)) == 6:
                    is_brand = True
                result_brand = mongo.collection.distinct("brand",
                                                         {"system_code": {"$regex": f"^{str(system_code)[:2]}"}})
                brands_dict = [{"name": brand, "label": redis_db.client.hget(brand, "fa_ir"),
                                "route": brand.replace(" ", ""),
                                "system_code": db_data_getter({"brand": brand, "model": None}).get(
                                    "system_code"),
                                "active": (
                                    True if str(system_code) == db_data_getter({"brand": brand, "model": None}).get(
                                        "system_code") else False) if is_brand else False} for brand in result_brand]

                result = mongo.collection.find({"system_code": {"$regex": f"^{system_code}"}}, {"_id": 0}).skip(
                    skips).limit(per_page)
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
            def db_data_getter(query):
                result = mongo.kowsar_collection.find_one(query, {"_id": 0})
                return result if result else {}

            with RedisConnection() as redis_db:
                result_Accessory = mongo.collection.distinct("sub_category", {"main_category": "Accessory"})
                category_list_Accessory = [{"name": category, "label": redis_db.client.hget(category, "fa_ir"),
                                            "route": category.replace(" ", ""),
                                            "system_code": db_data_getter(
                                                {"sub_category": category, "brand": None}).get("system_code")
                                            } for
                                           category in result_Accessory]

                result_main_category = mongo.collection.distinct("main_category")
                category_list_main_category = [
                    {"name": category, "label": redis_db.client.hget(category, "fa_ir"),
                     "route": category.replace(" ", ""),
                     "system_code": db_data_getter({"main_category": category, "sub_category": None}).get(
                         "system_code")}
                    for category in result_main_category]

                result_brand = mongo.collection.distinct("brand", {"sub_category": "Mobile"})
                category_list_brand = [{"name": brand, "label": redis_db.client.hget(brand, "fa_ir"),
                                        "route": brand.replace(" ", ""),
                                        "system_code": db_data_getter({"brand": brand, "model": None}).get(
                                            "system_code")} for brand in
                                       result_brand]

                result_latest_product = list(mongo.collection.find(
                    {"sub_category": "Mobile", "products": {"$ne": None}, "visible_in_site": True,
                     "products.visible_in_site": True},
                    {"_id": 0, "system_code": 1, "name": 1,
                     "products": {
                         "$elemMatch": {"visible_in_site": True},
                     },
                     "route": "$name"
                     }).sort("date", -1).limit(20))
                for i in result_latest_product:
                    i['route'] = i['route'].replace(" ", "")
                return {
                    "categories": {
                        "label": "دسته بندی",
                        "items": category_list_main_category},
                    "mobile": {
                        "label": "برند های موبایل",
                        "items": category_list_brand},
                    "accessory": {
                        "label": "دسته بندی لوازم جانبی",
                        "items": category_list_Accessory},
                    "product": {
                        "label": "جدیدترین محصولات",
                        "items": result_latest_product
                    }
                }

    @staticmethod
    def get_product_attributes(system_code):
        with MongoConnection() as mongo:
            result = mongo.collection.find_one({"products.system_code": system_code}, {"_id": 0})
            if result:
                out_data = {
                    "name": result['name'],
                    "system_code": result['system_code'],
                    "brand": result['brand'],
                    "mainCategory": result['main_category'],
                    "model": result['model'],
                    "subCategory": result['sub_category'],
                }

                db_attribute = mongo.attributes_collection.find({}, {"_id": 0})
                result_attribute = list()
                for obj in db_attribute:
                    if obj.get("set_to_nodes"):
                        len_parent = len(obj.get("parent")) if obj.get("parent") else 0
                        if system_code[:len_parent] == obj.get("parent"):
                            result_attribute.append(obj)
                    else:
                        if obj.get("parent") == system_code:
                            result_attribute.append(obj)

                if result_attribute:
                    out_data.update({
                        "attributes": result_attribute
                    })
                    return out_data, True
                return "attribute not found", False
            return "product not found", False

    @staticmethod
    def get_product_list_back_office(brands, warehouses, price, sellers, colors, quantity, date,
                                     guarantees, steps, visible_in_site, approved, available, page,
                                     per_page):
        with MongoConnection() as mongo:
            colors_list = mongo.collection.distinct("products.config.color")
            brands_list = mongo.collection.distinct("brand")
            warehouses_list = list()
            seller_list = mongo.collection.distinct("products.config.seller")
            guarantee_list = mongo.collection.distinct("products.config.guarantee")
            step_list = mongo.collection.distinct("products.step")

            skip = (page - 1) * per_page
            limit = per_page

            query = dict()
            if brands:
                query["brand"] = {"$in": brands}
            if warehouses:
                query["warehouse"] = {"$in": warehouses}
            if price:
                query["products.price"] = {"$gte": price[0], "$lte": price[1]}
            if sellers:
                query["products.config.seller"] = {"$in": sellers}
            if colors:
                query["products.config.color"] = {"$in": colors}
            if quantity:
                query["products.quantity"] = {"$gte": quantity[0], "$lte": quantity[1]}
            if date:
                query["date"] = {"$gte": date[0], "$lte": date[1]}
            if guarantees:
                query["products.config.guarantee"] = {"$in": guarantees}
            if steps:
                query["products.step"] = {"$in": steps}
            if visible_in_site:
                query["visible_in_site"] = visible_in_site
            if approved:
                query["approved"] = approved

            db_result = mongo.collection.find(query, {"_id": 0}).skip(skip).limit(limit)
            return {
                "filters": [
                    {
                        "name": "brands",
                        "label": "برند",
                        "input_type": "multi_select",
                        "options": brands_list
                    },
                    {
                        "name": "colors",
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
                        "name": "sellers",
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
                        "name": "guarantees",
                        "label": "گارانتی",
                        "input_type": "multi_select",
                        "options": guarantee_list
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
                        "options": step_list
                    }
                ],
                "products": list(db_result)
            }

    @staticmethod
    def step_up_product(system_code):
        with MongoConnection() as mongo:
            mongo.collection.update_one({"products.system_code": system_code}, {"$inc": {"products.$.step": 1}})
        return True

    @staticmethod
    def get_product_child(system_code, lang):
        with MongoConnection() as mongo:
            db_result = mongo.collection.find_one({"products.system_code": system_code}, {"_id": 0,
                                                                                          "system_code": 1,
                                                                                          "name": 1,
                                                                                          "products": {"$elemMatch": {
                                                                                              "system_code": system_code}}})
            if db_result:
                name = db_result.get("name")
                parent_system_code = db_result.get("system_code")
                product = db_result.get("products")[0]
                with RedisConnection() as redis_db:
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
                return {
                    "name": name,
                    "parent_system_code": parent_system_code,
                    "product": product
                }

            return None

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

    def __init__(self, system_code, name, url_name):
        self.system_code = system_code
        self.name = name
        self.url_name = url_name
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

    @staticmethod
    def edit_product(system_code, data):
        with MongoConnection() as mongo:
            visible_in_site = data.get("visible_in_site")
            result = mongo.collection.update_one({"system_code": system_code, "products.step": 5},
                                                 {"$set": {"visible_in_site": visible_in_site}})
            if result.modified_count:
                return {"message": "product visibility updated successfully",
                        "label": "وضعیت نمایش محصول با موفقیت بروزرسانی شد"}
            return {"message": "product visibility update failed",
                    "label": "بروزرسانی وضعیت نمایش محصول با خطا مواجه شد"}


class CreateChild(Product):

    def __init__(self, system_code, parent_system_code):
        self.system_code = system_code
        self.parent_system_code = parent_system_code
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
                        db_data = mongo.collection.find_one({"products.system_code": obj['system_code']},
                                                            {"_id": 0, "products": {
                                                                "$elemMatch": {"system_code": obj['system_code']}}})
                        obj['visibleInSite'] = db_data.get("products", [])[0].get("visible_in_site",
                                                                                  False) if db_data else False
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

    @staticmethod
    def edit_product(system_code, data):
        with MongoConnection() as mongo:
            visible_in_site = data.get("visible_in_site")
            result = mongo.collection.update_one({"products.system_code": system_code, "products.step": 5},
                                                 {"$set": {"products.$.visible_in_site": visible_in_site}})
            if result.modified_count:
                return True
            return False


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
                                                 {"$set": {"products.$.attributes": self.attributes,
                                                           "products.$.step": 3}})
            if result.modified_count:
                return {"message": "attribute added successfully", "label": "صفت با موفقیت اضافه شد"}, True
            return {"error": "attribute add failed", "label": "فرایند افزودن صفت به مشکل برخورد"}, False

    def delete(self) -> tuple:
        pass
