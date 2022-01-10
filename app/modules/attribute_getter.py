from app.helpers.mongo_connection import MongoConnection


def attribute_setter(attributes: dict) -> bool:
    with MongoConnection() as mongo:
        for attribute in attributes:
            if attribute.get("set_to_nodes"):
                re = "^" + attribute.get("parent")
                mongo.kowsar_collection.update_many({"system_code": {"$regex": re}},
                                                    {"$push": {"attributes": attribte}}, upsert=True)
            else:
                mongo.kowsar_collection.update_one({"system_code": attribte.get("parent")},
                                                   {"$push": {"attributes": attribte}}, upsert=True)
    return True
