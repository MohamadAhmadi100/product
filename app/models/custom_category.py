from app.helpers.mongo_connection import MongoConnection


class KowsarCategories:
    def __init__(self, system_code, custom_name, visible_in_site, image):
        self.system_code = system_code
        self.custom_name = custom_name
        self.visible_in_site = visible_in_site
        self.image = image

    def create(self, category_label):
        with MongoConnection() as mongo:
            result = mongo.kowsar_collection.update_many({'system_code': {"$regex": "^" + self.system_code}},
                                                         {'$set': {category_label: self.custom_name
                                                                   }})
            visible_result = mongo.kowsar_collection.update_one({'system_code': self.system_code},
                                                                {'$set': {'visible_in_site': self.visible_in_site,
                                                                          'image': self.image
                                                                          }})
            if result.modified_count > 0 and visible_result.modified_count > 0:
                return True
            elif result.matched_count > 0 and visible_result.matched_count > 0:
                return "Category already exists"
            return None
