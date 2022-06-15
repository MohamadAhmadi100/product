from abc import ABC, abstractmethod

from app.helpers.date_convertor import jalali_now, gregorian_now
from app.helpers.mongo_connection import MongoConnection
from app.helpers.redis_connection import RedisConnection
from app.modules.translator import RamStorageTranslater


# from app.validators.attribute_validator import attribute_validator


class Product(ABC):

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

                                for key, value in product['attributes'].items():
                                    stored_data = [attr for attr in attributes_data if attr['name'] == key][0]
                                    stored_data['value'] = value
                                    attributes_list.append(stored_data)

                                product['attributes'] = attributes_list

                                visible_products.append(product)

                        result['products'] = visible_products
                        kowsar_data = mongo.kowsar_collection.find_one({"system_code": system_code[:9]}, {"_id": 0})
                        result.update({
                            "routes": {
                                "route": result.get('main_category'),
                                "label": kowsar_data.get('main_category_label'),
                                "system_code": system_code[:2],
                                "child": {
                                    "route": result.get('sub_category'),
                                    "label": kowsar_data.get('sub_category_label'),
                                    "system_code": system_code[:4],
                                    "child": {
                                        "route": result.get('brand'),
                                        "label": kowsar_data.get('brand_label'),
                                        "system_code": system_code[:6]
                                    }
                                }
                            }
                        })
                    return result
            return None

    @staticmethod
    def get_product_list_by_system_code(system_code, page, per_page, available_quantities):
        with MongoConnection() as mongo:
            def db_data_getter(query):
                result = mongo.kowsar_collection.find_one(query, {"_id": 0})
                return result if result else {}

            skips = per_page * (page - 1)
            result_brand = mongo.collection.distinct("brand",
                                                     {"system_code": {"$regex": f"^{str(system_code)[:2]}"},
                                                      "visible_in_site": True})
            brands_list = list()
            for brand in result_brand:
                brand_data = db_data_getter({"brand": brand, "system_code": {"$regex": "^.{6}$"}})
                brands_list.append({"name": brand, "label": brand_data.get("brand_label"),
                                    "route": brand.replace(" ", ""),
                                    "system_code": brand_data.get(
                                        "system_code"),
                                    })

            result = mongo.collection.find({"system_code": {"$in": list(available_quantities.keys())}},
                                           {"_id": 0}).skip(skips).limit(per_page)
            product_list = list()
            for product in result:
                if product.get("visible_in_site"):
                    if product.get('products'):
                        colors = [color['config']['color'] for color in product['products'] if
                                  color.get("visible_in_site")]
                        product.update({"colors": colors})
                        image = [child.get('attributes', {}).get('mainImage-pd') for child in product['products'] if
                                 child.get('attributes', {}).get('mainImage-pd')]
                        image = image[0] if image else None
                        product.update({"image": image})
                        del product['products']

                        if colors:
                            product_list.append(product)

            return {"brands": brands_list, "products": product_list}

    @staticmethod
    def get_category_list(available_quantities):
        with MongoConnection() as mongo:
            def db_data_getter(query):
                result = mongo.kowsar_collection.find_one(query, {"_id": 0})
                return result if result else {}

            result_Accessory = mongo.collection.distinct("sub_category",
                                                         {"main_category": "Accessory", "visible_in_site": True})
            category_list_Accessory = list()
            for category in result_Accessory:
                kowsar_data = db_data_getter({"sub_category": category, "system_code": {"$regex": "^.{6}$"}})
                category_list_Accessory.append({"name": category, "label": kowsar_data.get("sub_category_label"),
                                                "route": category.replace(" ", ""),
                                                "system_code": kowsar_data.get("system_code"),
                                                "image": kowsar_data.get("image"),
                                                })

            result_main_category = mongo.collection.distinct("main_category", {"visible_in_site": True})
            category_list_main_category = list()
            for category in result_main_category:
                kowsar_data = db_data_getter({"main_category": category, "system_code": {"$regex": "^.{2}$"}})
                category_list_main_category.append(
                    {"name": category, "label": kowsar_data.get("main_category_label"),
                     "route": category.replace(" ", ""),
                     "system_code": kowsar_data.get("system_code"),
                     "image": kowsar_data.get("image")
                     }
                )

            result_brand = mongo.collection.distinct("brand", {"sub_category": "Mobile", "visible_in_site": True})
            category_list_brand = list()

            for brand in result_brand:
                kowsar_data = db_data_getter({"brand": brand, "system_code": {"$regex": "^.{6}$"}})
                category_list_brand.append(
                    {"name": brand, "label": kowsar_data.get("brand_label"),
                     "route": brand.replace(" ", ""),
                     "system_code": kowsar_data.get("system_code"),
                     "image": kowsar_data.get("image")
                     })

            result_latest_product = list(mongo.collection.find(
                {"sub_category": "Mobile", "products": {"$ne": None}, "visible_in_site": True,
                 "system_code": {"$in": list(available_quantities.keys())},
                 "products.visible_in_site": True},
                {"_id": 0, "system_code": 1, "name": 1,
                 "products": {
                     "$elemMatch": {"visible_in_site": True},
                 },
                 "route": "$name"
                 }).sort("products.date", -1).limit(20))

            product_list = list()
            for product in result_latest_product:
                product['route'] = product['route'].replace(" ", "")
                colors = [color['config']['color'] for color in product['products'] if
                          color.get("visible_in_site")]
                product.update({"colors": colors})
                image = [child.get('attributes', {}).get('mainImage-pd') for child in product['products'] if
                         child.get('attributes', {}).get('mainImage-pd')]
                image = image[0] if image else None
                product.update({"image": image})
                del product['products']

                product_list.append(product)

            result_latest_product = product_list
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
    def get_product_list_back_office(brands, sellers, colors, date,
                                     guarantees, steps, visible_in_site, approved, available, page,
                                     per_page, system_codes_list, lang):
        with MongoConnection() as mongo, RedisConnection() as redis_db:
            colors_list = [{"value": i, "label": redis_db.client.hget(i, lang)} for i in
                           mongo.collection.distinct("products.config.color")]
            brands_list = [{"value": i, "label": redis_db.client.hget(i, lang)} for i in
                           mongo.collection.distinct("brand")]
            warehouses_list = list()
            seller_list = [{"value": i, "label": redis_db.client.hget(i, lang)} for i in
                           mongo.collection.distinct("products.config.seller")]
            guarantee_list = [{"value": i, "label": redis_db.client.hget(i, lang)} for i in
                              mongo.collection.distinct("products.config.guarantee")]
            step_list = mongo.collection.distinct("products.step")

            skip = (page - 1) * per_page
            limit = per_page

            query = {
                "archived": {"$ne": True},
            }
            if brands:
                query["brand"] = {"$in": brands}
            if sellers:
                query["products.config.seller"] = {"$in": sellers}
            if colors:
                query["products.config.color"] = {"$in": colors}
            if date:
                query["date"] = {}
                if date[0]:
                    query["date"]["$gt"] = date[0]
                if date[1]:
                    query["date"]["$lt"] = date[1]

            if guarantees:
                query["products.config.guarantee"] = {"$in": guarantees}
            if steps:
                query["products.step"] = {"$in": steps}
            if visible_in_site:
                query["visible_in_site"] = visible_in_site
            if approved:
                query["approved"] = approved
            if system_codes_list:
                query["system_code"] = {"$in": system_codes_list}

            query['products.$.archived'] = {'$ne': True}

            len_db = len(list(mongo.collection.find(query, {"_id": 1})))
            db_result = list(mongo.collection.find(query, {"_id": 0}).skip(skip).limit(limit))

            product_list = list()
            for parent in db_result:
                childs = list()
                for child in parent.get("products", []):
                    if not child.get("archived"):
                        for key, value in child['config'].items():
                            label = redis_db.client.hget(value, lang) if key != "images" else None
                            child['config'][key] = RamStorageTranslater(value,
                                                                        lang).translate() if key == "storage" or key == "ram" else label

                        childs.append(child)
                parent.update({"products": childs})
                product_list.append(parent)
            filters = [
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
            ]
            return {
                "filters": filters,
                "result_len": len_db,
                "products": product_list
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
        with MongoConnection() as mongo:
            result = mongo.collection.update_one({"system_code": self.system_code},
                                                 {"$set": {"archived": True,
                                                           "visible_in_site": False,
                                                           }})
            if result.modified_count:
                return {"message": "product archived successfully", "label": "محصول با موفقیت حذف شد"}, True
            return {"message": "product failed to archive", "label": "حذف محصول با خطا مواجه شد"}, False

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
                                                 {"$set": {"products.$.archived": True,
                                                           "products.$.visible_in_site": False}})
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
            stored_data = mongo.collection.find_one({"products.system_code": self.system_code, },
                                                    {"_id": 0, "products": {
                                                        "$elemMatch": {"system_code": self.system_code}}})
            db_action = {"$set": {"products.$.attributes": self.attributes}}
            if stored_data.get("products", [])[0].get("step") == 2:
                db_action["$set"]["products.$.step"] = 3

            result = mongo.collection.update_one({"products.system_code": self.system_code}, db_action)
            if result.modified_count:
                return {"message": "attribute added successfully", "label": "صفت با موفقیت اضافه شد"}, True
            return {"error": "attribute add failed", "label": "فرایند افزودن صفت به مشکل برخورد"}, False

    def delete(self) -> tuple:
        pass
