from app.helpers.mongo_connection import MongoConnection


class KowsarCategories:
    def __init__(self, system_code, custom_name, visible_in_site, image):
        self.system_code = system_code
        self.custom_name = custom_name
        self.visible_in_site = visible_in_site
        self.image = image

    def create(self):
        with MongoConnection() as mongo:
            if len(self.system_code) == 2:
                result = mongo.kowsar_collection.update_many({'system_code': {"$regex": "^" + self.system_code}},
                                                             {'$set': {'main_category_label': self.custom_name
                                                                       }})
                visible_result = mongo.kowsar_collection.update_many({'system_code': self.system_code},
                                                                     {'$set': {'visible_in_site': self.visible_in_site,
                                                                               'image': self.image
                                                                               }})
                if result.modified_count <= 0 and visible_result.modified_count <= 0:
                    return True

            elif len(self.system_code) == 4:
                result = mongo.kowsar_collection.update_many({'system_code': {"$regex": "^" + self.system_code}},
                                                             {'$set': {'sub_category_label': self.custom_name
                                                                       }})
                visible_result = mongo.kowsar_collection.update_many({'system_code': self.system_code},
                                                                     {'$set': {'visible_in_site': self.visible_in_site,
                                                                               'image': self.image
                                                                               }})
                if result.modified_count <= 0 and visible_result.modified_count <= 0:
                    return True

            elif len(self.system_code) == 6:
                result = mongo.kowsar_collection.update_many({'system_code': {"$regex": "^" + self.system_code}},
                                                             {'$set': {'brand_label': self.custom_name
                                                                       }})
                visible_result = mongo.kowsar_collection.update_many({'system_code': self.system_code},
                                                                     {'$set': {'visible_in_site': self.visible_in_site,
                                                                               'image': self.image
                                                                               }})
                if result.modified_count <= 0 and visible_result.modified_count <= 0:
                    return True
            else:
                return None
