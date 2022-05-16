import jdatetime

from app.helpers.mongo_connection import MongoConnection


class KowsarCategories:
    def __init__(self, system_code, custom_name, visible_in_site, image):
        self.system_code = system_code
        self.custom_name = custom_name
        self.visible_in_site = visible_in_site
        self.image = image

    def create(self, category_label):
        """
        Do Database Insertion
        """
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


class CustomCategories:
    def __init__(self, name, products, label, visible_in_site, image):
        self.name = name
        self.products = products
        self.label = label
        self.visible_in_site = visible_in_site
        self.image = image
        self.created_at = jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def is_unique(self):
        """
        Check if category already exists
        """
        with MongoConnection() as mongo:
            result = mongo.custom_category.find_one({'name': self.name})
            if result:
                return False
            return True

    def create(self):
        """
        Do Database Insertion
        """
        with MongoConnection() as mongo:
            result = mongo.custom_category.insert_one(self.__dict__)
            if result.inserted_id:
                return True
            return None
