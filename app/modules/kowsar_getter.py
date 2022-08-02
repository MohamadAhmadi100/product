import os
import re

import xlrd

from app.helpers.exception_handler import exception_handler
from app.helpers.mongo_connection import MongoConnection


class KowsarGetter:
    KALA_FILE_NAME = "کالا.xls"
    GRUHE_KALA_FILE_NAME = "گروه کالا.xls"

    def __init__(self):
        self.main_category_dict = {}  # -> {'10': 'Device', '11': 'Component', ...}
        self.sub_category_dict = {}  # -> {'1001': 'Mobile', '1002': 'Tablet', ...}
        self.brand_category_dict = {}  # -> {'100101': 'Mobile Sumsung', '100102': 'Mobile Apple ', ...}
        self.model_dict = {}  # -> {'100101001': 'A260 ', '100101002': 'A01 ', ...}
        self.config_dict = {}  # -> {'100104021006': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'}, ...}

    def read_excel(self, file_name: str):
        import app.data as files  # data path -> __init__.py
        file = os.path.dirname(files.__file__) + '/' + file_name
        sheet = xlrd.open_workbook(file).sheet_by_index(0)
        return sheet

    @exception_handler
    def product_group_getter(self):
        '''
        This function will set self.main_category_dict: {system_code: Main Category}
        , self.sub_category_dict: {system_code: Sub Category}
        , self.brand_category_dict: {system_code: Brand}
        , self.model_dict: {system_code: Model}
        '''
        sheet = self.read_excel(file_name=self.GRUHE_KALA_FILE_NAME)
        for col in range(1, sheet.nrows):
            group_code = sheet.cell(col, 0).value
            group_name = sheet.cell(col, 1).value.strip()
            # TODO: in python 3.10 we can do this with match-case
            if len(group_code) == 2:  # main_category
                self.main_category_dict[group_code] = group_name
            elif len(group_code) == 4:  # sub_category
                self.sub_category_dict[group_code] = group_name
            elif len(group_code) == 6:  # brand
                group_name = group_name.replace(self.sub_category_dict[group_code[:4]] + " ", "")
                group_name = group_name if not group_name == 'Sumsung' else 'Samsung'
                self.brand_category_dict[group_code] = group_name
            elif len(group_code) == 9:  # model
                self.model_dict[group_code] = group_name

    def product_config_getter(self):
        '''
        This function will get name and config of the product from the excel file
        and return two lists:
        1- name_config_code_with_bracket: [system_code, name and config separated with bracket]
        2- name_config_code_with_bracket: [system_code, name and config without separation!]
        '''
        sheet = self.read_excel(file_name=self.KALA_FILE_NAME)
        ignore_list = ['Disable', 'Test', 'تست']
        name_config_code_with_bracket = []
        name_config_code_without_bracket = []
        for col in range(1, sheet.nrows):
            name_config = sheet.cell(col, 2).value
            valid_name_config = True
            for item in ignore_list:
                if item in name_config:
                    valid_name_config = False
            if valid_name_config and '[' in name_config:
                name_config_code_with_bracket.append([sheet.cell(col, 1).value, name_config])
            elif valid_name_config and '[' not in name_config:
                name_config_code_without_bracket.append([sheet.cell(col, 1).value, name_config])
        return name_config_code_with_bracket, name_config_code_without_bracket

    '''
    This function will return configs_list: [system_code, model, config]
    It will also set self.configs which will later be used for configs bag-of-words(BOW)
    '''

    def name_config_separator(
            self, name_config_code_with_bracket: list, name_config_code_without_bracket: list
    ) -> tuple:
        '''
        This function will return configs_list: [system_code, model, config]
        It will also set self.configs which will later be used for configs bag-of-words(BOW)
        '''
        configs_list = list()
        configs = list()
        for x in name_config_code_with_bracket:
            system_code = x[0]
            model = self.model_dict.get(x[0][:9])
            config = x[1].split("[")[1].lower().replace("]", "")  # split with [ and remove ]
            configs.append(config)
            configs_list.append([system_code, model, config])
        for x in name_config_code_without_bracket:
            system_code = x[0]
            model = self.model_dict.get(x[0][:9])
            name_config_without_whitespace = x[1].lower().replace(" ", "")
            last_word_in_model = model.lower().split()[-1]
            # use the last word in model to find the separation between name and config
            start_index = name_config_without_whitespace.find(last_word_in_model) + len(last_word_in_model)
            config = name_config_without_whitespace[start_index:].replace("]", "")
            configs.append(config)
            configs_list.append([system_code, model, config])
        return configs_list, configs

    @staticmethod
    def bag_of_words(configs) -> dict:
        '''
        This function will return a dictionary with the words in configs as keys
        We should set values to 'color', 'guarantee', ... and use the dictionary for finding configs
        '''
        words_set = set()
        for x in configs:
            words_set.update(x.replace("-", " ").split())
        words_dict = {}
        for x in words_set:
            words_dict[x] = ''
        return words_dict

    @staticmethod
    def bag_of_words_organizer(words_dict):
        '''
        This function will get the words_dict and change keys to values and vice versa
        Then the result should use as a reference for finding configs
        '''
        new_dict = {}
        for key, value in words_dict.items():
            if value not in new_dict.keys():
                new_dict[value] = [key]
            else:
                if key not in new_dict[value]:
                    new_dict[value].append(key)
        return new_dict

    @staticmethod
    def config_matcher(conf, new_conf, conf_dict, keyword):
        '''
        This function will check if configs are in the bag of words
        and if it was, add the config to the new_conf
        '''
        for key in conf_dict.get(keyword):
            if key in conf:
                if keyword == "storage" or keyword == "ram":
                    if "t" in key:
                        new_conf[keyword] = str(list(map(int, re.findall(r'\d+', key)))[0]) + " TB"
                    elif "m" in key:
                        new_conf[keyword] = str(list(map(int, re.findall(r'\d+', key)))[0]) + " MB"
                    else:
                        new_conf[keyword] = str(list(map(int, re.findall(r'\d+', key)))[0]) + " GB"
                else:
                    new_conf[keyword] = key
                conf = conf.replace(key, "")
                break
        return conf

    @staticmethod
    def check_conf_is_empty(conf):
        '''
        This function will check if there is any word in conf
        '''
        return conf.replace("-", "").replace(" ", "") == ""

    def configs_list_maker(self, conf_dict_sample, conf_list):
        '''
        This function will set self.config_dict: {system_code: [configs]}
        '''
        for x in conf_list:
            system_code = x[0]
            config = x[2]
            new_conf = {}
            for key in conf_dict_sample.keys():
                if key == 'ignore_case':
                    config = self.config_matcher(config, new_conf.copy(), conf_dict_sample, key)
                else:
                    config = self.config_matcher(config, new_conf, conf_dict_sample, key)
                if self.check_conf_is_empty(config):
                    self.config_dict[system_code] = new_conf
                    break

            config = config.replace("-", "").replace(" ", "")
            if config == "":
                self.config_dict[system_code] = new_conf
                continue
            if system_code.startswith('1205'):  # power bank
                new_conf['capacity'] = config
            elif config and new_conf.get('storage') is None:
                if re.findall(r'\d+', config):
                    new_conf['storage'] = str(list(map(int, re.findall(r'\d+', config)))[0]) + " GB"
            self.config_dict[system_code] = new_conf

    def add_seller(self, sellers):
        for system_code in self.config_dict.keys():
            seller = sellers.get(self.config_dict.get(system_code, {}).get('guarantee', ""))
            seller = seller if seller else "Aasood"
            self.config_dict[system_code]['seller'] = seller

    def check_storage_ram(self):
        """
        if ram is bigger than storage it swap them
        """
        for system_code, configs in self.config_dict.items():
            config_keys = configs.keys()
            if "storage" in config_keys and "ram" in config_keys:
                if "TB" not in configs['storage'] and "MB" not in configs['storage']:
                    storage = configs['storage'].replace(" GB", "")
                    ram = configs['ram'].replace(" GB", "")
                    if int(ram) > int(storage):
                        configs['storage'] = f"{ram} GB"
                        configs['ram'] = f"{storage} GB"

    @staticmethod
    def create_new_parents():
        new_parents = dict()
        with MongoConnection() as mongo:
            mongo.parent_col.drop()
            db_data = list(mongo.kowsar_collection.find({"system_code": {"$regex": "^[\s\S]{12,}$"}}, {"_id": 0}))
            for obj in db_data:
                system_code = obj.get('system_code')
                parent_schema = {'system_code': f'{system_code[:9]}01',
                                 "main_category": obj.get('main_category'),
                                 "sub_category": obj.get('sub_category'),
                                 "brand": obj.get('brand'),
                                 "model": obj.get('model'),
                                 "attributes": {
                                     "storage": obj.get('config', {}).get('storage'),
                                     "ram": obj.get('config', {}).get('ram')
                                 }
                                 }
                if system_code[:9] in new_parents.keys():
                    storage_rams = [(a['attributes']['storage'], a['attributes']['ram']) for a in
                                    new_parents[system_code[:9]]]
                    if (obj.get('config', {}).get('storage'), obj.get('config', {}).get('ram')) not in storage_rams:
                        index = len(new_parents[system_code[:9]]) + 1
                        parent_schema[
                            "system_code"] = f"{system_code[:9]}{index}" if index > 9 else f'{system_code[:9]}0{index}'
                        new_parents[system_code[:9]].append(parent_schema)
                else:
                    new_parents[system_code[:9]] = [parent_schema]
            insert_db = []
            for i in new_parents.values():
                insert_db.extend(i)
            mongo.parent_col.insert_many(insert_db)
            return True

    @staticmethod
    def system_code_items_getter(system_code: str):
        """
        return items in the system_code
        """
        with MongoConnection() as client:
            if system_code == "00":
                regex = "^[1-9][0-9]$"
                label = "main_category"
            elif len(system_code) == 2:
                label = "sub_category"
                regex = '^' + system_code + ".{4}$"
            elif len(system_code) == 6:
                label = "brand"
                regex = '^' + system_code + ".{3}$"
            elif len(system_code) == 9:
                label = "model"
                regex = '^' + system_code + ".{4}$"
            elif len(system_code) == 13:
                label = "configs"
                regex = '^' + system_code + ".{3}$"
            elif len(system_code) == 16:
                products = list(client.kowsar_collection.aggregate([
                    {"$match": {'system_code': {'$regex': "^" + system_code + ".{9}$"}}},
                    {"$project": {"_id": 0}}
                ]))
                return products
            else:
                return None
            products = list(client.kowsar_collection.aggregate([
                {"$match": {'system_code': {'$regex': regex}}},
                {"$project": {"_id": 0, "system_code": 1, "label": f"${label}"}}
            ]))
            return products

    @staticmethod
    def system_code_name_getter(system_code):
        """
        return name or config of the system_code
        """
        with MongoConnection() as client:
            data = client.kowsar_collection.find_one({'system_code': system_code}, {"_id": 0})
            return data

    @exception_handler
    def update_kowsar_collection(self):
        """
        This function will update kowsar_collection with new data
        """
        with MongoConnection() as mongo:
            for system_code in self.config_dict.keys():
                mongo.kowsar_collection.update_one(
                    {'system_code': system_code},
                    {"$set": {
                        "system_code": system_code,
                        "main_category": self.main_category_dict.get(system_code[:2]),
                        "sub_category": self.sub_category_dict.get(system_code[:4]),
                        "brand": self.brand_category_dict.get(system_code[:6]),
                        "model": self.model_dict.get(system_code[:9]),
                        "config": self.config_dict.get(system_code)}
                    },
                    upsert=True)

            for system_code in self.model_dict.keys():
                mongo.kowsar_collection.update_one(
                    {'system_code': system_code},
                    {"$set":
                         {"system_code": system_code,
                          "main_category": self.main_category_dict.get(system_code[:2]),
                          "sub_category": self.sub_category_dict.get(system_code[:4]),
                          "brand": self.brand_category_dict.get(system_code[:6]),
                          "model": self.model_dict.get(system_code)}
                     },
                    upsert=True)
            for system_code in self.brand_category_dict.keys():
                mongo.kowsar_collection.update_one(
                    {'system_code': system_code},
                    {"$set":
                         {"system_code": system_code,
                          "main_category": self.main_category_dict.get(system_code[:2]),
                          "sub_category": self.sub_category_dict.get(system_code[:4]),
                          "brand": self.brand_category_dict.get(system_code)}
                     },
                    upsert=True)
            for system_code in self.sub_category_dict.keys():
                mongo.kowsar_collection.update_one(
                    {'system_code': system_code},
                    {"$set":
                         {"system_code": system_code,
                          "main_category": self.main_category_dict.get(system_code[:2]),
                          "sub_category": self.sub_category_dict.get(system_code)}
                     },
                    upsert=True)
            for system_code in self.main_category_dict.keys():
                mongo.kowsar_collection.update_one(
                    {'system_code': system_code},
                    {"$set":
                         {"system_code": system_code,
                          "main_category": self.main_category_dict.get(system_code)}
                     },
                    upsert=True)

    @staticmethod
    def get_parents(system_code):
        with MongoConnection() as mongo:
            return mongo.parent_col.find_one({'system_code': system_code}, {"_id": 0})

    def product_getter(self):
        """
        This function will get product details from local dict
        """
        self.product_group_getter()
        name_configs_codes_with_brackets, name_configs_codes_without_brackets = self.product_config_getter()
        config_list, configs = self.name_config_separator(name_configs_codes_with_brackets,
                                                          name_configs_codes_without_brackets)
        conf_dict_sample = {
            'storage': ['512gb', '512 gb', '256gb', '256 gb', '128gb', '128 gb', '64gb', '64 gb', '32gb', '32 gb',
                        '16gb', '16 gb', '1gb', '1 gb', '32mg', '1tb', '1 tb', '2tb', '2 tb', '4tb', '4 tb', '5tb',
                        '5 tb'],
            'color': ['dark blue', 'white/blue', 'haze silver', 'iceberg blue', 'gold coffe', 'gold black',
                      'rose gold',
                      'black/red', 'ocean blue', 'white red', 'white/red',
                      'black/blue', 'black red', 'orange', 'breathing crystal', 'white', 'green', 'blue',
                      'black', 'color', 'gray', 'violet', 'gold',
                      'silver', 'red', 'pink', 'bronze', 'purple', 'yellow', 'charcoal', 'brown', 'mix',
                      'aura glow',
                      'coral', 'boronz', 'dark nebula', 'olive', 'cyan', 'rose', 'dusk', 'military', 'sand',
                      'dark night', 'bedone rang', 'ice', 'titanium', 'fjord', "Peach", "Mint"],
            'guarantee': ['sherkati 01', 'sherkati', 'aban digi', 'abandigi', 'life time', 'awat', 'asli', 'nog',
                          'sazgar', 'nabeghe'],
            'ram': ['16gb', '12gb', '8gb', '6gb', '4gb', '3gb', '2gb', '1gb'],
            'network': ['5g', '4g'],
            'capacity': ['20k', '10000mah', '10k', '2600mah', '6800mah', '20100 mah', '10400mah', '5000mah'],
            'sim': ['dual sim'],
            'year': ['2018', '2019', '2020'],
            'type': ['wireless', 'wireless headphones'],
            'power': ['10w', '18w'],
            'part_number': ['zaa'],
            'processor': ['7020u'],
            'ignore_case': ['case', 'glass', 'headphones', 'smart band', 'smart watch', 'i3', 'intel', 'tamam']
        }
        seller_sample = {
            "sherkati 01": "همراه غرب",
            "sherkati": "تجارت خانه حاجی قاسم",
            "aban digi": "آبان دیجی",
            "abandigi": "آبان دیجی",
            "life time": "آسود",
            "awat": "آوات",
            "asli": "آسود",
            "nog": "آسود",
            "sazgar": "آوات",
            "nabeghe": "نابغه",
        }
        seller_sample = {
            "sherkati 01": "Aasood",
            "sherkati": "Aasood",
            "aban digi": "Aban Digi",
            "abandigi": "Aban Digi",
            "life time": "Aasood",
            "awat": "Aasood",
            "asli": "Aasood",
            "nog": "Aasood",
            "sazgar": "Awat",
            "nabeghe": "Nabeghe",
        }
        self.configs_list_maker(conf_dict_sample, config_list)
        self.add_seller(seller_sample)
        self.check_storage_ram()
