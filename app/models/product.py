from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, validator

from app.helpers.mongo_connection import MongoConnection
from app.validators.attribute_validator import attribute_validator


class Product(BaseModel):
    system_code: str
    name: Optional[str]
    step: Optional[int]
    main_category: Optional[str]
    sub_category: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    config: Optional[dict]
    attributes: Optional[dict] = {}

    class Config:
        schema_extra = {
            "example": {
                "system_code": "100104021006",
                "attributes": {
                    "image": "/src/default.jpg",
                    "year": 2020
                }
            }
        }

    @validator('system_code')
    def system_code_validator(cls, value):
        if not isinstance(value, str):
            raise HTTPException(status_code=417, detail={"error": 'system_code must be a string'})
        elif 2 > len(value) or len(value) > 12:
            raise HTTPException(status_code=417, detail={"error": "system_code must be between 2 and 12 characters"})
        return value

    @validator('attributes')
    def attributes_validator(cls, value):
        # TODO: needs attention!
        if not isinstance(value, dict):
            raise HTTPException(status_code=417, detail={"error": "attributes must be a dictionary"})
        return value

    def save_as_object(self, result) -> None:
        self.system_code = result.get('system_code')
        self.main_category = result.get('main_category')
        self.sub_category = result.get('sub_category')
        self.brand = result.get('brand')
        self.model = result.get('model')
        self.config = result.get('config')
        self.name = result.get('name')
        self.step = result.get('step')
        self.attributes = result.get('attributes')

    def set_kowsar_data(self, data: dict) -> None:
        self.main_category = data.get('main_category')
        self.sub_category = data.get('sub_category')
        self.brand = data.get('brand')
        self.model = data.get('model')
        self.config = data.get('config')

    def create(self) -> tuple:
        """
        Adds a product to main collection in database.
        The system_code of the product should be unique!
        """
        with MongoConnection() as mongo:
            kowsar_data = mongo.kowsar_collection.find_one({'system_code': self.system_code}, {'_id': 0})
            if not kowsar_data:
                return {"error": "product not found in kowsar"}, False
            self.set_kowsar_data(kowsar_data)
            self.attributes = {}
            self.del_null()
            result = mongo.collection.insert_one(self.dict())
        if result.inserted_id:
            return {"message": "product created successfully"}, True
        return {"error": "product creation failed"}, False

    def check_parent(self):
        with MongoConnection() as mongo:
            sys_code = self.system_code if self.step == 3 else self.system_code[:9]
            data = mongo.collection.find_one({'system_code': sys_code})
            return True if data else False

    def add_attributes(self):
        with MongoConnection() as mongo:
            result = mongo.collection.update_one({"system_code": self.system_code},
                                                 {"$set": {"step": self.step,
                                                           "attributes": self.attributes}})
            if result.modified_count:
                return {"message": "attribute added successfully"}, True
            return {"error": "attribute add failed"}, False

    def get(self, system_code: str = None, page: int = 1, per_page: int = 10):
        with MongoConnection() as mongo:
            if not system_code:
                skips = per_page * (page - 1)
                data = mongo.collection.find({}, {'_id': 0}).skip(skips).limit(per_page)
                return list(data)
            result = mongo.collection.find_one({'system_code': system_code}, {'_id': 0})
            if result:
                self.save_as_object(result)
                return self
            return None

    def delete(self) -> tuple:
        with MongoConnection() as mongo:
            result = mongo.collection.delete_one({"system_code": self.system_code})
            if result.deleted_count:
                return {"message": "product deleted successfully"}, True
            return {"error": "product deletion failed"}, False

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

    def del_null(self):
        product_object = self.dict()
        for attribute in product_object.keys():
            if not product_object[attribute]:
                delattr(self, attribute)

