from abc import ABC, abstractmethod
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

from app.helpers.mongo_connection import MongoConnection
from app.validators.attribute_validator import attribute_validator
from app.helpers.redis_connection import RedisConnection
from app.modules.translator import RamStorageTranslater


class Product(ABC):
    @classmethod
    def class_attributes(cls):
        return cls.__dict__.get("__annotations__").keys()

    def class_attributes_getter(self):
        keys = self.class_attributes()
        dict_data = dict()
        for key in keys:
            db_key = key
            if key[0] == "_":
                db_key = key.replace("_", "", 1)
            exec(f"dict_data['{db_key}'] = self.{key}")
        return dict_data

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
            with RedisConnection() as redis_db:
                if result and result.get('products'):
                    for product in result['products']:
                        for key, value in product['config'].items():
                            label = redis_db.client.hget(value, lang) if key != "images" else None
                            product['config'][key] = {
                                "attribute_label": redis_db.client.hget(key, lang),
                                "label": RamStorageTranslater(value,
                                                              lang).translate() if key == "storage" or key == "ram" else label
                            }
                            if key == "images":
                                del product['config'][key]['label']
                                del product['config'][key]['label']

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


class CreateParent(BaseModel, Product):
    system_code: str = Field(
        ..., title="شناسه محصول", maxLength=11, minLength=11, placeholder="10010402101", isRequired=True
    )
    name: Optional[str] = Field(
        None, title="نام", minLength=3, maxLength=256, placeholder="ردمی ۹ سی", isRequired=False
    )
    visible_in_site: bool
    _main_category: Optional[str]
    _sub_category: Optional[str]
    _brand: Optional[str]
    _model: Optional[str]
    _attributes: Optional[dict]

    @validator('system_code')
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "system code must be a string",
                "label": "کد سیستمی باید از نوع رشته باشد"
            })
        elif len(value) != 11:
            raise HTTPException(status_code=417, detail={
                "error": "system_code must be 11 characters",
                "label": "طول شناسه محصول باید ۱۱ کاراکتر باشد"
            })
        return value

    @validator('name')
    def name_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": 'name must be a string',
                "label": "اسم باید از نوع رشته باشد"
            })
        elif len(value) < 3 or len(value) > 256:
            raise HTTPException(status_code=417, detail={
                "error": "name must be between 3 and 256 characters",
                "label": "طول اسم باید میان ۳ تا ۲۵۶ کاراکتر باشد"
            })
        return value

    @validator('visible_in_site')
    def visible_in_site_validator(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={
                "error": 'visible_in_site must be a boolean',
                "label": "نمایش در سایت باید از نوع بولی باشد"
            })
        return value

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

    @classmethod
    def set_kowsar_data(cls, data: dict) -> None:
        cls._main_category = data.get('main_category')
        cls._sub_category = data.get('sub_category')
        cls._brand = data.get('brand')
        cls._model = data.get('model')
        cls._attributes = data.get('attributes')

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
            result = mongo.collection.insert_one(self.class_attributes_getter())
        if result.inserted_id:
            return {"message": "product created successfully", "label": "محصول با موفقیت ساخته شد"}, True
        return {"error": "product creation failed", "label": "فرایند ساخت محصول به مشکل خورد"}, False

    def delete(self) -> tuple:
        pass


class CreateChild(BaseModel, Product):
    parent_system_code: str = Field(
        ..., title="شناسه محصول", maxLength=11, minLength=11, placeholder="10010402101", isRequired=True
    )
    system_code: str = Field(
        ..., title="شناسه محصول", maxLength=12, minLength=12, placeholder="100104021006", isRequired=True
    )
    visible_in_site: bool
    _config: Optional[dict]

    @validator('system_code')
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "system codes must be a string",
                "label": "شناسه های محصولات باید از نوع رشته باشد"
            })
        elif len(value) != 12:
            raise HTTPException(status_code=417, detail={
                "error": "system_code must be 12 characters",
                "label": "طول شناسه محصول باید ۱۲ کاراکتر باشد"
            })
        return value

    @validator('visible_in_site')
    def visible_in_site_validator(cls, value):
        if not isinstance(value, bool):
            raise HTTPException(status_code=417, detail={
                "error": 'visible_in_site must be a boolean',
                "label": "نمایش در سایت باید از نوع بولی باشد"
            })
        return value

    @classmethod
    def set_kowsar_data(cls, data: dict) -> None:
        cls._config = data.get('config')

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
            product = self.class_attributes_getter()
            product.pop("parent_system_code")
            result = mongo.collection.update_one(
                {"system_code": self.parent_system_code},
                {'$addToSet': {'products': product}})
        if result.modified_count:
            return {"message": "product created successfully", "label": "محصول با موفقیت ساخته شد"}, True
        return {"error": "product creation failed", "label": "فرایند ساخت محصول به مشکل خورد"}, False

    @staticmethod
    def suggester(data, system_code, config):
        with MongoConnection() as mongo:
            sugested_products = list()
            system_codes = mongo.collection.distinct("products.system_code", {"system_code": system_code})
            for obj in data:
                if obj['system_code'] in system_codes:
                    obj['created'] = True
                if obj.get('label').get('storage') == config[0] and obj.get('label').get('ram') == config[1]:
                    sugested_products.append(obj)
            return sugested_products

    def delete(self) -> tuple:
        with MongoConnection() as mongo:
            result = mongo.collection.update_one({"products.system_code": self.system_code},
                                                 {"$set": {"products.$.archived": True}})
            if result.modified_count:
                return {"ok": True}, True
            return {"ok": False}, False


class AddAtributes(BaseModel, Product):
    system_code: str = Field(
        ..., title="شناسه محصول", maxLength=12, minLength=12, placeholder="100104021006", isRequired=True
    )
    attributes: dict

    def system_code_is_unique(self) -> bool:
        with MongoConnection() as mongo:
            result = mongo.collection.find_one({'products.system_code': self.system_code})
            return False if result else True

    def validate_attributes(self):
        with MongoConnection() as mongo:
            result = mongo.kowsar_collection.find_one({'system_code': self.system_code})
            attributes_from_collection = result.get("attributes")
            if attributes_from_collection:
                item = attribute_validator(attributes_from_collection, self)
                self = item
            else:
                pass

    def create(self) -> tuple:
        with MongoConnection() as mongo:
            result = mongo.collection.update_one({"products.system_code": self.system_code},
                                                 {"$set": {"products.$.attributes": self.attributes}})
            if result.modified_count:
                return {"message": "attribute added successfully", "label": "صفت با موفقیت اضافه شد"}, True
            return {"error": "attribute add failed", "label": "فرایند افزودن صفت به مشکل برخورد"}, False

    def delete(self) -> tuple:
        pass
