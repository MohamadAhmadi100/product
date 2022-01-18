from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator, Field

from app.helpers.mongo_connection import MongoConnection
from app.validators.attribute_validator import attribute_validator


class Product(BaseModel):
    system_code: str = Field(
        ..., title="کد سیستمی", maxLength=12, minLength=9, placeholder="100104021006", isRequired=True
    )
    name: Optional[str] = Field(
        "", title="نام", minLength=3, maxLength=256, placeholder="ردمی ۹ سی", isRequired=False
    )
    _step: int
    _main_category: Optional[str]
    _sub_category: Optional[str]
    _brand: Optional[str]
    _model: Optional[str]
    _config: Optional[dict]
    attributes: Optional[dict] = Field({}, title="صفت ها", maxLength=256, isRequired=False)

    @validator('system_code')
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={
                "error": "system code must be a string",
                "label": "کد سیستمی باید از نوع رشته باشد"
            })
        elif 2 > len(value) or len(value) > 12:
            raise HTTPException(status_code=417, detail={
                "error": "system_code must be between 2 and 12 characters",
                "label": "طول کد سیستمی باید میان ۲ تا ۱۲ کاراکتر باشد"
            })
        return value

    @validator('attributes')
    def attributes_validator(cls, value):
        # TODO: needs attention!
        if not isinstance(value, dict):
            raise HTTPException(status_code=417, detail={
                "error": "attributes must be a dictionary",
                "label": "صفت ها باید از نوع دیکشنری باشند"
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

    @classmethod
    def step_setter(cls, value):
        cls._step = value

    @classmethod
    def class_attributes(cls):
        return cls.__dict__.get("__annotations__").keys()

    def class_attributes_getter(self, keys):
        dict_data = dict()
        for key in keys:
            db_key = key
            if key != "system_code":
                db_key = key.replace("_", "")
            exec(f"dict_data['{db_key}'] = self.{key}")
        return dict_data

    @classmethod
    def save_as_object(cls, result) -> None:
        cls.system_code = result.get('system_code')
        cls._main_category = result.get('main_category')
        cls._sub_category = result.get('sub_category')
        cls._brand = result.get('brand')
        cls._model = result.get('model')
        cls._config = result.get('config')
        cls.name = result.get('name')
        cls._step = result.get('step')
        cls.attributes = result.get('attributes')

    @classmethod
    def set_kowsar_data(cls, data: dict) -> None:
        cls._main_category = data.get('main_category')
        cls._sub_category = data.get('sub_category')
        cls._brand = data.get('brand')
        cls._model = data.get('model')
        cls._config = data.get('config')

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
            result = mongo.collection.insert_one(self.class_attributes_getter(self.class_attributes()))
        if result.inserted_id:
            return {"message": "product created successfully", "label": "محصول با موفقیت ساخته شد"}, True
        return {"error": "product creation failed", "label": "فرایند ساخت محصول به مشکل خورد"}, False

    def check_parent(self):
        with MongoConnection() as mongo:
            sys_code = self.system_code if self._step == 3 else self.system_code[:9]
            data = mongo.collection.find_one({'system_code': sys_code})
            return True if data else False

    def add_attributes(self):
        with MongoConnection() as mongo:
            result = mongo.collection.update_one({"system_code": self.system_code},
                                                 {"$set": {"step": self._step,
                                                           "attributes": self.attributes}})
            if result.modified_count:
                return {"message": "attribute added successfully", "label": "صفت با موفقیت اضافه شد"}, True
            return {"error": "attribute add failed", "label": "فرایند افزودن صفت به مشکل برخورد"}, False

    @staticmethod
    def get(system_code: str = None, page: int = 1, per_page: int = 10):
        with MongoConnection() as mongo:
            if not system_code:
                skips = per_page * (page - 1)
                re = '^[0-9]{9}$'
                data = mongo.collection.find({'system_code': {'$regex': re}}, {'_id': 0}).skip(skips).limit(per_page)
                return list(data)
            re = '^' + system_code
            result = mongo.collection.find({'system_code': {'$regex': re}}, {"_id": 0})
            return list(result)

    def get_object(self, system_code):
        with MongoConnection() as mongo:
            result = mongo.collection.find_one({"system_code": system_code}, {"_id": 0})
            if result:
                self.save_as_object(result)
                return self
            return None

    def delete(self) -> tuple:
        with MongoConnection() as mongo:
            result = mongo.collection.delete_one({"system_code": self.system_code})
            if result.deleted_count:
                return {"message": "product deleted successfully", "label": "محصول با موفقیت حذف شد"}, True
            return {"error": "product deletion failed", "label": "فرایند حذف محصول به مشکل برخورد"}, False

    def system_code_is_unique(self) -> bool:
        with MongoConnection() as mongo:
            result = mongo.collection.find_one({'system_code': self.system_code})
            return False if result else True

    def validate_attributes(self):
        with MongoConnection() as mongo:
            result = mongo.kowsar_collection.find_one({'system_code': self.system_code})
            attributes_from_collection = result.get("attributes")
            if attributes_from_collection:
                item = attribute_validator(attributes_from_collection, self)
                self = item
            else:
                delattr(self, "attributes")

    @staticmethod
    def suggester(data):
        with MongoConnection() as mongo:
            kowsar_system_codes = [obj.get("system_code") for obj in data]
            query = {"$or": [{"system_code": item} for item in kowsar_system_codes]}
            stored_data = mongo.collection.find(query, {"_id": 0})
            stored_system_codes = [obj.get('system_code') for obj in list(stored_data)]
            for item in data:
                if item.get('system_code') in stored_system_codes:
                    item['created'] = True
            return data
