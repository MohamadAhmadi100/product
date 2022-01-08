from pydantic import BaseModel, validator

from app.helpers.mongo_connection import MongoConnection
from app.module.validation_of_attributes import Validates
from app.module.kowsar_getter import KowsarGetter
from app.module.attributes import Attributes


class Product(BaseModel):
    system_code: str
    specification: dict

    class Config:
        schema_extra = {
            "example": {
                "system_code": "120301001001",
                "specification": {"country": "iran"}
            }
        }

    @validator('system_code')
    def system_code_validator(cls, value):
        if type(value) is not str:
            raise ValueError('system_code must be a string')
        elif 2 >= len(value) >= 255:
            raise ValueError('system_code must be between 2 and 255 characters')
        return value

    @validator('specification')
    def specification_validator(cls, value):
        if type(value) is not dict:
            raise ValueError('specification must be a dictionary')

    def save_as_object(self, result) -> None:
        self.system_code = result.get('system_code')
        self.specification = result.get('specification')

    def create(self) -> tuple:
        """
            Adds a product to main collection in database.
            The system_code of the product should be unique!
        """
        system_code_generator = KowsarGetter()
        system_code_generator.product_getter()
        data = system_code_generator.system_code_name_getter(self.system_code)  # get data from system code
        spec = Validates.attribute_validation(system_code=self.system_code, attr_names=self.specification)
        req = dict()
        req['system_code'] = self.system_code
        req_list = ['config', 'model', 'brand', 'sub_category', 'main_category']
        for i in req_list:
            req[i] = data.get(i)
        with MongoConnection() as mongo:
            attrs = mongo.attribute_kowsar_collection.find({}, {'_id': 0})
            for attr in attrs:
                if attr.get('system_code') == self.system_code:
                    if attr.get('attributes'):
                        for i in attr.get('attributes'):
                            for k, v in spec.items():
                                if i.get('name') == k:
                                    req[i.get('name')] = v
            mongo.collection.insert_one(req)
            result = mongo.collection.insert_one(self.dict())
            if result.inserted_id:
                return {"message": "product created successfully"}, True
            return {"error": "product creation failed"}, False

    def get(self, attribute_name: str = None, page: int = 1, per_page: int = 10):
        with MongoConnection() as mongo:
            if not attribute_name:
                skips = per_page * (page - 1)
                data = mongo.collection.find({}, {'_id': 0}).skip(skips).limit(per_page)
                return list(data)
            result = mongo.collection.find_one({'system_code': self.system_code}, {'_id': 0})
            if result:
                self.save_as_object(result)
                return self
            return None

    def update(self, data) -> tuple:
        with MongoConnection() as mongo:
            spec = Validates.attribute_validation(system_code=self.system_code, attr_names=data)
            result = mongo.collection.update_one({"name": self.system_code}, {"$set": spec})
            if result.modified_count:
                return {"message": "product updated successfully"}, True
            return {"error": "product update failed"}, False

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


class Assignees:
    @staticmethod
    def get_all_attributes_from_attribute_api():
        return Attributes.get_attributes()

    @staticmethod
    def set_all_attributes_by_set_to_nodes():
        return Attributes.set_attribute_by_set_to_nodes()

    @staticmethod
    def get_all_attribute_by_system_code(system_code: str):
        with MongoConnection() as mongo:
            attrs = mongo.attribute_kowsar_collection.find_one({'system_code': system_code}, {'_id': 0})
            return [i.get('name') for i in attrs.get('attributes')]