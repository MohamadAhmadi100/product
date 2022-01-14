from app.helpers.mongo_connection import MongoConnection


def attribute_setter(attributes: list) -> bool:
    with MongoConnection() as mongo:
        for attribute in attributes:
            if attribute.get("set_to_nodes"):
                re = "^" + attribute.get("parent")
                mongo.kowsar_collection.update_many({"system_code": {"$regex": re}},
                                                    {"$addToSet": {"attributes": attribute}}, upsert=True)
            else:
                mongo.kowsar_collection.update_one({"system_code": attribute.get("parent")},
                                                   {"$addToSet": {"attributes": attribute}}, upsert=True)
    return True
