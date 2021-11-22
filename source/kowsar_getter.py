import os
import sys

sys.path.append("..")

import xlrd

from source.mongo_connection import MongoConnection


class KowsarGetter:
    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.main_category_dict = {}
        self.sub_category_dict = {}
        self.brand_category_dict = {}
        self.model_dict = {}
        self.configs = []
        self.config_dict = {}

    def read_excel(self, file_name: str):
        file = self.dir_path + '/' + file_name
        sheet = xlrd.open_workbook(file).sheet_by_index(0)
        return sheet

    def product_group_getter(self):
        sheet = self.read_excel(file_name='گروه کالا.xls')
        for col in range(1, sheet.nrows):
            group_code = sheet.cell(col, 0).value
            group_name = sheet.cell(col, 1).value
            try:
                # in python 3.10 we can do this with match-case
                if len(group_code) == 2:
                    self.main_category_dict[group_code] = group_name
                elif len(group_code) == 4:
                    self.sub_category_dict[group_code] = group_name
                elif len(group_code) == 6:
                    self.brand_category_dict[group_code] = group_name
                elif len(group_code) == 9:
                    self.model_dict[group_code] = group_name
            except Exception as e:
                print(e)

    def product_config_getter(self):
        sheet = self.read_excel(file_name='kala.xls')
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

    def name_config_separator(self, name_config_code_with_bracket: list,
                              name_config_code_without_bracket: list) -> list:
        configs_list = list()
        for x in name_config_code_with_bracket:
            system_code = x[0]
            model = self.model_dict.get(x[0][:9])
            config = x[1].split("[")[1].lower().replace("]", "")
            self.configs.append(config)
            configs_list.append([system_code, model, config])
        for x in name_config_code_without_bracket:
            system_code = x[0]
            model = self.model_dict.get(x[0][:9])
            name_config_without_whitespace = x[1].lower().replace(" ", "")
            last_word_in_model = model.lower().split()[-1]
            start_index = name_config_without_whitespace.find(last_word_in_model) + len(last_word_in_model)
            config = name_config_without_whitespace[start_index:].replace("]", "")
            self.configs.append(config)
            configs_list.append([system_code, model, config])
        return configs_list

    def bag_of_words(self) -> dict:
        words_list = list()
        for x in self.configs:
            words_list.extend(x.replace("-", " ").split())
        words_dict = {}
        for x in words_list:
            if not words_dict.get(x):
                words_dict[x] = ''
        return words_dict  # set values to 'color', 'guarantee' and ...

    @staticmethod
    def bag_of_words_organizer(words_dict):
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
        for key in conf_dict.get(keyword):
            if key in conf:
                new_conf[keyword] = key
                conf = conf.replace(key, "")
                break
        return conf, new_conf

    @staticmethod
    def check_conf_is_empty(conf):
        return conf.replace("-", "").replace(" ", "") == ""

    def configs_list_maker(self, conf_dict_sample, conf_list):
        for x in conf_list:
            system_code = x[0]
            config = x[2]
            new_conf = {}
            for key in conf_dict_sample.keys():
                if key == 'ignore_case':
                    config, ignore_conf = self.config_matcher(config, new_conf, conf_dict_sample, key)
                else:
                    config, new_conf = self.config_matcher(config, new_conf, conf_dict_sample, key)
                if self.check_conf_is_empty(config):
                    self.config_dict[system_code] = new_conf
                    break

            config = config.replace("-", "").replace(" ", "")
            if config == "":
                self.config_dict[system_code] = new_conf
                continue
            if system_code.startswith('1205'):  # power bank
                new_conf['capacity'] = config
            elif new_conf.get('storage') is None:
                new_conf['storage'] = config
            self.config_dict[system_code] = new_conf

    @staticmethod
    def config_code_getter(system_code):
        with MongoConnection() as client:
            data = client.kowsar_name_collection.find_one(
                {'system_code': system_code[:12]}, {"_id": 0}
            )
            return data

    @staticmethod
    def model_code_getter(system_code):
        with MongoConnection() as client:
            data = client.kowsar_name_collection.find_one({'system_code': system_code[:9]}, {"_id": 0})
            return data

    @staticmethod
    def brand_category_code_getter(system_code):
        with MongoConnection() as client:
            data = client.kowsar_name_collection.find_one({'system_code': system_code[:6]}, {"_id": 0})
            return data

    @staticmethod
    def sub_category_code_getter(system_code):
        with MongoConnection() as client:
            data = client.kowsar_name_collection.find_one({'system_code': system_code[:4]}, {"_id": 0})
            return data

    @staticmethod
    def main_category_code_getter(system_code):
        with MongoConnection() as client:
            data = client.kowsar_name_collection.find_one({'system_code': system_code[:2]}, {"_id": 0})
            return data

    @staticmethod
    def main_category_items_getter(system_code):
        with MongoConnection() as client:
            re = '^' + system_code[:2]
            data = client.kowsar_name_collection.find({'system_code': {'$regex': re}}, {"_id": 0})
            products = [product for product in data if len(product['system_code']) == 4]
            return products

    @staticmethod
    def sub_category_items_getter(system_code):
        with MongoConnection() as client:
            re = '^' + system_code[:4]
            data = client.kowsar_name_collection.find({'system_code': {'$regex': re}}, {"_id": 0})
            products = [product for product in data if len(product['system_code']) == 6]
            return products

    @staticmethod
    def brand_category_items_getter(system_code):
        with MongoConnection() as client:
            re = '^' + system_code[:6]
            data = client.kowsar_name_collection.find({'system_code': {'$regex': re}}, {"_id": 0})
            products = [product for product in data if len(product['system_code']) == 9]
            return products

    @staticmethod
    def model_items_getter(system_code):
        with MongoConnection() as client:
            re = '^' + system_code[:9]
            data = client.kowsar_name_collection.find({'system_code': {'$regex': re}}, {"_id": 0})
            products = [product for product in data if len(product['system_code']) == 12]
            return products

    def update_kowsar_name_collection(self):
        with MongoConnection() as client:
            for system_code in self.config_dict.keys():
                if client.kowsar_name_collection.count_documents({'system_code': system_code}) == 0:
                    client.kowsar_name_collection.insert_one(
                        {'system_code': system_code, 'config': self.config_dict.get(system_code),
                         'model': self.model_dict.get(system_code[:9]),
                         'brand': self.brand_category_dict.get(system_code[:6]),
                         'sub_category': self.sub_category_dict.get(system_code[:4]),
                         'main_category': self.main_category_dict.get(system_code[:2])}
                    )

        with MongoConnection() as client:
            for system_code in self.model_dict.keys():
                if client.kowsar_name_collection.count_documents({'system_code': system_code}) == 0:
                    client.kowsar_name_collection.insert_one(
                        {'system_code': system_code, 'model': self.model_dict.get(system_code),
                         'brand': self.brand_category_dict.get(system_code[:6]),
                         'sub_category': self.sub_category_dict.get(system_code[:4]),
                         'main_category': self.main_category_dict.get(system_code[:2])}
                    )
            for system_code in self.brand_category_dict.keys():
                if client.kowsar_name_collection.count_documents({'system_code': system_code}) == 0:
                    client.kowsar_name_collection.insert_one(
                        {'system_code': system_code, 'brand': self.brand_category_dict.get(system_code),
                         'sub_category': self.sub_category_dict.get(system_code[:4]),
                         'main_category': self.main_category_dict.get(system_code[:2])}
                    )
            for system_code in self.sub_category_dict.keys():
                if client.kowsar_name_collection.count_documents({'system_code': system_code}) == 0:
                    client.kowsar_name_collection.insert_one(
                        {'system_code': system_code, 'sub_category': self.sub_category_dict.get(system_code),
                         'main_category': self.main_category_dict.get(system_code[:2])}
                    )
            for system_code in self.main_category_dict.keys():
                if client.kowsar_name_collection.count_documents({'system_code': system_code}) == 0:
                    client.kowsar_name_collection.insert_one(
                        {'system_code': system_code,
                         'main_category': self.main_category_dict.get(system_code)}
                    )

    def product_getter(self):
        self.product_group_getter()
        name_configs_codes_with_brackets, name_configs_codes_without_brackets = self.product_config_getter()
        config_list = self.name_config_separator(name_configs_codes_with_brackets,
                                                 name_configs_codes_without_brackets)
        conf_dict_sample = {
            'storage': ['512gb', '512 gb', '256gb', '256 gb', '128gb', '128 gb', '64gb', '64 gb', '32gb', '32 gb',
                        '16gb', '16 gb', '1gb', '1 gb', '32mg', '1tb', '1 tb', '2tb', '2 tb', '4tb', '4 tb', '5tb',
                        '5 tb'],
            'color': ['dark blue', 'white/blue', 'haze silver', 'iceberg blue', 'gold coffe', 'gold black', 'rose gold',
                      'black/red', 'ocean blue', 'white red', 'white/red',
                      'black/blue', 'black red', 'orange', 'breathing crystal', 'white', 'green', 'blue',
                      'black', 'color', 'gray', 'violet', 'gold',
                      'silver', 'red', 'pink', 'bronze', 'purple', 'yellow', 'charcoal', 'brown', 'mix', 'aura glow',
                      'coral', 'boronz', 'dark nebula', 'olive', 'cyan', 'rose', 'dusk', 'military', 'sand',
                      'dark night', 'bedone rang', 'ice', 'titanium', 'fjord'],
            'guarantee': ['sherkati 01', 'sherkati', 'aban digi', 'abandigi', 'life time', 'awat', 'asli', 'nog',
                          'sazgar',
                          'nabeghe'],
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
        self.configs_list_maker(conf_dict_sample, config_list)
