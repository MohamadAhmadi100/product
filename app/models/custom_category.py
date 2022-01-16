from app.helpers.mongo_connection import MongoConnection
from pydantic import BaseModel, validator


class CustomCategory(BaseModel):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "atish bazi"
            }
        }

    @validator("name")
    def name_validator(cls, value):
        if not isinstance(value, str):
            raise ValueError('name must be a string')
        elif 3 > len(value) or len(value) > 128:
            raise ValueError('system_code must be between 3 and 128 characters')
        return value

    def add_product(self, product: dict):
        with MongoConnection() as mongo:
            result = mongo.custom_category.update_one({"name": self.name}, {"$addToSet": {"products": product}},
                                                      upsert=True)
            if result.upserted_id or result.modified_count:
                return {f'message': f'product assigned to {self.name} successfully'}, True
            return {'error': 'product assignment failed'}, False

    def remove_product(self, product):
        with MongoConnection() as mongo:
            result = mongo.custom_category.update_one({"name": self.name}, {"$pull": {"products": product}})
            if result.modified_count:
                return {f'message': f'product removed from {self.name} successfully'}, True
            return {'error': 'product removal failed'}, False

    def get_products(self):
        with MongoConnection() as mongo:
            result = mongo.custom_category.find_one({"name": self.name}, {"_id": 0})
            if result:
                return result.get("products")
            return None

    @staticmethod
    def get_custom_categories():
        with MongoConnection() as mongo:
            result = mongo.custom_category.find({}, {"_id": 0, "products": 0})
            return [category.get("name") for category in list(result)]

    def update_product_from_custom_category(self, product) -> tuple:
        with MongoConnection() as mongo:
            result = mongo.custom_category.update_one(
                {"name": self.name, 'products.system_code': product.get("system_code")},
                {"$set": {
                    'products.$': product}})
            if result.modified_count:
                return {"message": "product updated successfully"}, True
            return {"error": "product updated failed"}, False
