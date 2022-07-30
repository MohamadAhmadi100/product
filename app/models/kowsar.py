import requests

from app.helpers.mongo_connection import MongoConnection


class KowsarPart:
    def __init__(self, system_code, storage_ids, parent_system_code, guaranty):
        self.system_code = system_code
        self.storage_ids = storage_ids
        self.parent_system_code = parent_system_code
        self.guaranty = guaranty

    def create_kowsar_part(self, name, storage_ids, system_code):
        request_data = {
            "PartPartStoreDTOLst": [{"inv_Store_Code": str(i)} for i in storage_ids],
            "PartGroupCodeLst": [
                f"{self.model_code}"
            ],
            "prt_Part_Code": system_code,
            "prt_PartGroup_CodeMain": f"{self.model_code[:4]}",
            "prt_Part_Name": name,
            "prt_Part_HasQTYControl": True,
            "prt_PartUnit_Code": "2",
            "inv_PartClass_Code": f"{self.model_code[:2]}",
            "sel_PartCategory_Code": f"{self.model_code[:2]}",
            "gnr_Lookup_InternalIdDecIncrementGroup": "1",
            "gnr_Lookup_InternalIdSerialState": "2",
            "prt_Part_Sellable": "0"  # be 1 on production
        }
        result = requests.post("http://31.47.52.130:8099/PartService/Web/TryInsertPart2", json=request_data, headers={
            "UserName": "Site",
            "Password": "Site@3333"
        }).json()
        if not result.get("HasError", True):
            return True, result.get("prt_Part_Code")
        return False, None

    def is_unique(self):
        with MongoConnection() as mongo:
            result = mongo.new_kowsar_collection.find_one({"system_code": self.system_code})
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
            result = mongo.new_kowsar_collection.insert_one(
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
            result = mongo.new_kowsar_collection.find_one({"system_code": self.system_code})
            if result:
                return False
            return True

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
            "BackPack/HandyBag": "200032", "Cover/Case": "200033", "Screen Protector": "200034",
            "Stand/Holder": "200035", "USB HUB": "200036", "Cable": "200037",
            "Converter": "200038", "WebCam": "200039", "Mouse Pad": "200040",
            "Band": "200041", "Watch": "200042", "pen": "200043", "Game/Software": "200044",
            "Battery": "200045", "Cooling": "200046", "Power Port": "200047",
            "TV": "200048", "External DVD": "200049", "Gajet": "200050",
            "Modem": "200051", "Access Point": "200052", "Switch/Router": "200053",
            "Printer": "200054", "Scanner": "200055", "Copy-Machine": "200056",
            "Data Video Projector": "200057", "Telephone": "200058", "Fax": "200059",
            "Barcode Reader": "200060", "Cartridge": "200061", "Gaming": "200062", "Vacuum Cleaner": "200063"
        }

        if len(self.system_code) == 13:
            request_data['SaveAsFormalAcc'] = True
            accformal_name = parent_data.get("sub_category") if parent_data.get(
                "sub_category") not in ["Mobile", "t-mobile"] else "mobile"
            request_data['acc_FormalGrouping_NameMain'] = "گروهای کالا"
            request_data['acc_FormalAcc_Code'] = codes.get(accformal_name)

        result = requests.post("http://31.47.52.130:8099/PartService/Web/TryInsertPartGroup", json=request_data,
                               headers={
                                   "UserName": "Site",
                                   "Password": "Site@3333"
                               }).json()
        if not result.get("HasError", True):
            return True
        return False

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
            result = mongo.new_kowsar_collection.insert_one(data)
        if result.inserted_id:
            return True
        return False


class KowsarConfig:
    @staticmethod
    def is_unique(config_type, system_code):
        with MongoConnection() as mongo:
            result = mongo.kowsar_config.find_one(
                {"config_type": config_type, "system_code": system_code}, {"_id": 1})
            if result:
                return False
            return True

    @staticmethod
    def create_static_configs(config_type, system_code, name):
        with MongoConnection() as mongo:
            result = mongo.kowsar_config.insert_one(
                {"config_type": config_type, "system_code": system_code, "name": name})
        if result.inserted_id:
            return True
        return False

    @staticmethod
    def get_static_configs_by_config_type(config_type):
        with MongoConnection() as mongo:
            result = mongo.kowsar_config.find({"config_type": config_type}, {"_id": 0})
            return list(result)
