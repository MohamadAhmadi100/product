from app.helpers.mongo_connection import MongoConnection


class AttributesModules:
    @staticmethod
    def attribute_setter(attribute: dict) -> tuple:
        with MongoConnection() as mongo:
            result = mongo.attributes_collection.update_one({"name": attribute.get("name")},
                                                            {"$set": attribute}, upsert=True)
        if result.modified_count:
            return True, True
        elif result.upserted_id:
            return True, False
        return False, False

    @staticmethod
    def delete_attribute(attribute_name: str):
        with MongoConnection() as mongo:
            result = mongo.attributes_collection.delete_one({"name": attribute_name})

        if result.deleted_count:
            return True
        return False
