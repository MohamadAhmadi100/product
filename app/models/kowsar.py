import requests

from app.helpers.mongo_connection import MongoConnection


class KowsarGetter:
    @staticmethod
    def get_kowsar_system_code(system_code: str):
        """
        return items in the system_code
        """
        with MongoConnection() as client:
            if system_code == "00":
                query = {
                    "system_code": {"$regex": "^[1-9].{1}$"}
                }
                project = {
                    "_id": 0,
                    "system_code": 1,
                    "label": '$main_category'
                }
            elif len(system_code) == 2:
                query = {
                    "system_code": {"$regex": '^' + system_code + ".{4}$"}
                }
                project = {
                    "_id": 0,
                    "system_code": 1,
                    "label": '$sub_category'
                }
            elif len(system_code) == 6:
                query = {
                    "system_code": {"$regex": '^' + "[1-9]" + ".{8}$"}
                }
                project = {
                    "_id": 0,
                    "system_code": 1,
                    "label": '$brand',
                    "for_parent": {
                        "$cond": [{"$eq": [{"$substr": ['$system_code', 0, len(system_code)]}, system_code]}, True,
                                  False]}
                }
            elif len(system_code) == 9:
                query = {
                    "system_code": {"$regex": '^' + system_code + ".{4}$"}
                }
                project = {
                    "_id": 0,
                    "system_code": 1,
                    "label": '$model',
                }
            elif len(system_code) == 13:
                query = {
                    "system_code": {"$regex": '^' + system_code + ".{3}$"}
                }
                project = {
                    "_id": 0,
                    "system_code": 1,
                    "label": {'$reduce': {
                        'input': {"$objectToArray": "$configs"},
                        'initialValue': '',
                        'in': {
                            '$concat': [
                                '$$value',
                                {'$cond': [{'$eq': ['$$value', '']}, '', '-']},
                                '$$this.v']
                        }
                    }}
                }
            elif len(system_code) in [16, 19, 22]:
                query = {
                    "system_code": {"$regex": '^' + "[1-9]" + ".{%s}$" % (len(system_code) + 2)}
                }
                project = {
                    "_id": 0,
                    "system_code": {"$substr": ['$system_code', len(system_code), 3]},
                    "label": '$seller' if len(system_code) == 16 else '$color' if len(
                        system_code) == 19 else '$guaranty',
                    "for_parent": {
                        "$cond": [{"$eq": [{"$substr": ['$system_code', 0, len(system_code)]}, system_code]}, True,
                                  False]}
                }
            else:
                return None
            products = list(client.kowsar_collection.find(
                filter=query,
                projection=project
            ))

            if len(system_code) == 13:
                configs = client.kowsar_collection.find_one(
                    {"system_code": {"$regex": "^%s.{10}$" % (system_code[:6])}},
                    {"configs_keys": {
                        '$setIntersection': {
                            '$reduce': {
                                'input': {"$objectToArray": "$configs"},
                                'initialValue': [],
                                'in': {
                                    '$concatArrays': ['$$value', ['$$this.k']]
                                }
                            }
                        }
                    }})
                products = {
                    "data": products,
                    "configs": configs.get("configs_keys") if configs else None
                }
            elif len(system_code) in [6, 16, 19, 22]:
                brands_list = list()
                products.sort(key=lambda x: x['for_parent'], reverse=True)
                result = list()
                for product in products:
                    if product.get('label') not in brands_list:
                        product.update(
                            {"system_code": system_code + product.get('system_code')} if len(system_code) != 6 else {})
                        result.append(product)
                        brands_list.append(product.get('label'))
                products = result
            return products

    @staticmethod
    def system_code_items_getter(system_code: str):
        """
        return items in the system_code
        """
        with MongoConnection() as client:
            if system_code == "00":
                regex = ".{2}$"
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
                products = list(client.kowsar_collection.aggregate([
                    {"$match": {'system_code': {'$regex': regex}}},
                    {"$project": {"_id": 0, "system_code": 1, "label": f"${label}"}}
                ]))
                if products:
                    for product in products:
                        product['label'] = " ".join(product['label'].values())
                    return products
                return []
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

    @staticmethod
    def get_parents(system_code):
        with MongoConnection() as mongo:
            return mongo.parent_col.find_one({'system_code': system_code}, {"_id": 0})


class KowsarPart:
    def __init__(self, system_code, storage_ids, parent_system_code, guaranty):
        self.system_code = system_code
        self.storage_ids = storage_ids
        self.parent_system_code = parent_system_code
        self.guaranty = guaranty

    def log(self, response, success):
        with MongoConnection() as mongo:
            mongo.kowsar_log.insert_one({
                "log_type": "create_system_code",
                "success": success,
                "request": self.__dict__,
                "response": response
            })

    def create_kowsar_part(self, name, storage_ids, system_code):
        request_data = {
            "PartPartStoreDTOLst": [{"inv_Store_Code": str(i)} for i in storage_ids],
            "PartGroupCodeLst": [
                f"{self.parent_system_code[:16]}"
            ],
            "prt_Part_Code": system_code,
            "prt_PartGroup_CodeMain": f"{self.parent_system_code[:6]}",
            "prt_Part_Name": name,
            "prt_Part_HasQTYControl": True,
            "prt_PartUnit_Code": "2",
            "inv_PartClass_Code": f"{self.parent_system_code[:2]}",
            "sel_PartCategory_Code": f"{self.parent_system_code[:2]}",
            "gnr_Lookup_InternalIdDecIncrementGroup": "1",
            "gnr_Lookup_InternalIdSerialState": "2",
            "prt_Part_Sellable": "1"
        }
        try:
            response = requests.post("http://31.47.52.130:8099/PartService/Web/TryInsertPart2", json=request_data,
                                     headers={
                                         "UserName": "Site",
                                         "Password": "Site@3333"
                                     })
            response = response.json()
            result = True
        except:
            result = False
            response = response.text[1522:response.text.index(" The exception stack trace is:")]
        if result:
            return True, response
        return False, response

    def is_unique(self):
        with MongoConnection() as mongo:
            result = mongo.kowsar_collection.find_one({"system_code": self.system_code})
        if result:
            return False
        return True

    def name_getter(self):
        name = "["
        config_len = self.config.__len__() - 1
        count = 0
        for config, value in self.config.items():
            if count == config_len:
                name += f"{value}]"
            else:
                name += f"{value}-"
            count += 1
        return name

    def create_in_db(self, parent_data):
        with MongoConnection() as mongo:
            del parent_data["system_code"]
            result = mongo.kowsar_collection.insert_one(
                {
                    "system_code": self.system_code,
                    **parent_data,
                    "guaranty": self.guaranty,
                }
            )
        if result.inserted_id:
            return True
        return False


class KowsarGroup:
    def __init__(self, system_code, name, parent_system_code, configs):
        self.system_code = system_code
        self.name = name
        self.parent_system_code = parent_system_code
        self.configs = configs

    def is_unique(self):
        with MongoConnection() as mongo:
            result = mongo.kowsar_collection.find_one({"system_code": self.system_code})
            if result:
                return False
            return True

    def log(self, response, success):
        with MongoConnection() as mongo:
            mongo.kowsar_log.insert_one({
                "log_type": "create_kowsar_group",
                "success": success,
                "request": self.__dict__,
                "response": response
            })

    def create_kowsar_group(self, parent_data):
        request_data = {
            "prt_PartGroup_Code": self.system_code,
            "prt_PartGroup_CodeParent": self.parent_system_code,
            "prt_PartGroup_Name": self.name,
        }
        if not parent_data:
            del request_data['prt_PartGroup_CodeParent']
        codes = {
            "mobile": "200000", "Tablet": "200001", "Notebook": "200002",
            "All in One": "200003", "PC": "200004", "Server": "200005",
            "Game Console": "200006", "Camera": "200007", "CPU": "200008",
            "Motherboard": "200009", "Graphic Card": "200010", "RAM": "200011",
            "Internal HDD": "200012", "Internal DVD": "200013", "Internal SSD": "200014",
            "LAN Card": "200015", "Monitor": "200016", "Case": "200017",
            "Power Supply": "200018", "CPU FAN": "200019", "NB Battery": "200020",
            "External HDD": "200021", "External SSD": "200022", "Flash Memory": "200023",
            "Memory Card/Stick": "200024", "PowerBank": "200025", "Speaker": "200026",
            "Charger": "200027", "Mouse": "200028", "Keyboard": "200029",
            "Keyboard & Mouse": "200030", "Headphone/Headset/Hands Free": "200031",
            "Headphones": "200031",
            "BackPack/HandyBag": "200032", "Cover/Case": "200033", "Screen Protector": "200034",
            "Stand/Holder": "200035", "USB HUB": "200036", "Cable": "200037",
            "Converter": "200038", "WebCam": "200039", "Mouse Pad": "200040",
            "Band": "200041", "Watch": "200042", "pen": "200043", "Game/Software": "200044",
            "Battery": "200045", "Cooling": "200046", "Power Port": "200047",
            "TV": "200048", "External DVD": "200049", "Gajet": "200050",
            "Modem": "200051", "Access Point": "200052", "Switch/Router": "200053",
            "Printer": "200054", "Scanner": "200055", "Copy-Machine": "200056",
            "Data Video Projector": "200057", "Telephone": "200058", "Fax": "200059",
            "Barcode Reader": "200060", "Cartridge": "200061", "Gaming": "200062", "Vacuum Cleaner": "200063",
            "Laptop": "903434"
        }

        if len(self.system_code) == 16:
            request_data['SaveAsFormalAcc'] = True
            accformal_name = parent_data.get("sub_category") if parent_data.get(
                "sub_category") not in ["Mobile", "mobile"] else "mobile"
            request_data['acc_FormalGrouping_NameMain'] = "گروهای کالا"
            request_data['acc_FormalAcc_Code'] = codes.get(accformal_name)
        try:
            response = requests.post("http://31.47.52.130:8099/PartService/Web/TryInsertPartGroup", json=request_data,
                                     headers={
                                         "UserName": "Site",
                                         "Password": "Site@3333"
                                     })
            response = response.json()
            result = True
        except:
            result = False
            response = response.text[1522:response.text.index(" The exception stack trace is:")]
        if result:
            return True, response
        return False, response

    def category_name_getter(self, parent_data):
        if parent_data:
            if parent_data.get("image"):
                del parent_data["image"]
            if parent_data.get('visible_in_site'):
                del parent_data["visible_in_site"]

            parent_system_code_len = len(parent_data.get("system_code"))
            if parent_system_code_len == 2:
                parent_data['sub_category'] = self.name
            elif parent_system_code_len == 6:
                parent_data['brand'] = self.name
            elif parent_system_code_len == 9:
                parent_data['model'] = self.name
            elif parent_system_code_len == 13:
                parent_data['configs'] = self.configs
            elif parent_system_code_len == 16:
                parent_data['seller'] = self.name
            elif parent_system_code_len == 19:
                parent_data['color'] = self.name
            elif parent_system_code_len == 22:
                parent_data['guaranty'] = self.name

            parent_data['system_code'] = self.system_code
            return parent_data
        else:
            return {
                "system_code": self.system_code,
                "main_category": self.name
            }

    def create_in_db(self, data):
        with MongoConnection() as mongo:
            result = mongo.kowsar_collection.insert_one(data)
        if result.inserted_id:
            return True
        return False
