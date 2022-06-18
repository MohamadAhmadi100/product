import requests

from app.helpers.mongo_connection import MongoConnection


class KowsarPart:
    def __init__(self, model_code, config):
        self.model_code = model_code
        config = {k: v for k, v in config.items() if v}
        self.config = config

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
        # result = requests.post("http://31.47.52.130:8099/PartService/Web/TryInsertPart2", json=request_data, headers={
        #     "UserName": "Site",
        #     "Password": "Site@3333"
        # }).json()
        result = {
            "HasError": False,
            "prt_Part_Code": system_code,
        }
        if not result.get("HasError", True):
            return True, result.get("prt_Part_Code")
        return False, None

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

    def system_code_getter(self, model_code):
        with MongoConnection() as mongo:
            regex = f"^{model_code}."
            regex += "{3}"
            system_codes = mongo.kowsar_collection.distinct("system_code",
                                                            {"system_code": {"$regex": regex}})
            if system_codes:
                system_codes = [int(i[-3:]) for i in system_codes]
                system_codes.sort()
                system_code = system_codes[-1] + 1
                if system_code < 10:
                    system_code = f"00{system_code}"
                elif system_code < 100:
                    system_code = f"0{system_code}"
                else:
                    system_code = f"{system_code}"
            else:
                system_code = "001"

            return system_code

    def create_in_db(self, model_data, system_code):
        with MongoConnection() as mongo:
            del model_data["system_code"]
            result = mongo.kowsar_collection.insert_one(
                {
                    "system_code": system_code,
                    **model_data,
                    "config": self.config
                }
            )
        if result.inserted_id:
            return True
        return False


class KowsarGroup:
    def __init__(self, system_code, name, parent_system_code):
        self.system_code = system_code
        self.name = name
        self.parent_system_code = parent_system_code

    def is_unique(self):
        with MongoConnection() as mongo:
            result = mongo.kowsar_collection.find_one({"system_code": self.system_code})
            if result:
                return False
            return True

    def create_kowsar_group(self, parent_data):
        request_data = {
            "prt_PartGroup_Code": self.system_code,
            "prt_PartGroup_CodeParent": self.parent_system_code,
            "prt_PartGroup_Name": self.name,
        }
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
        if len(self.system_code) == 9:
            request_data['SaveAsFormalAcc'] = True
            accformal_name = parent_data.get("sub_category") if parent_data.get(
                "sub_category") != "Mobile" else "mobile"
            request_data['acc_FormalGrouping_NameMain'] = "گروهای کالا"
            request_data['acc_FormalAcc_Code'] = codes.get(accformal_name)

        result = requests.post("http://31.47.52.130:8099/PartService/Web/TryInsertPartGroup", json=request_data,
                               headers={
                                   "UserName": "Site",
                                   "Password": "Site@3333"
                               }).json()
        result = {
            "HasError": False
        }
        if not result.get("HasError", True):
            return True
        return False

    def category_name_getter(self, parent_data):
        if parent_data.get("image"):
            del parent_data["image"]
        if parent_data.get('visible_in_site'):
            del parent_data["visible_in_site"]

        system_code_len = len(parent_data.get("system_code"))
        if system_code_len == 2:
            parent_data['sub_category'] = self.name
        elif system_code_len == 4:
            parent_data['brand'] = self.name
        elif system_code_len == 6:
            parent_data['model'] = self.name

        parent_data['system_code'] = self.system_code
        return parent_data

    def create_in_db(self, data):
        with MongoConnection() as mongo:
            result = mongo.kowsar_collection.insert_one(data)
        if result.inserted_id:
            return True
        return False
