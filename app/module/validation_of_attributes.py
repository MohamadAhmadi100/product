from database.mongo_connection import MongoConnection
import datetime


class Validates:
    def __init__(self):
        pass

    @staticmethod
    def attribute_validation(attr_names: dict, system_code: str):
        with MongoConnection() as client:
            attrs = client.attribute_kowsar_collection.find_one({'system_code': system_code}, {'_id': 0})
            attributes = [i.get('name') for i in attrs.get('attributes')]
            for name in attributes:
                if name not in attr_names:
                    raise ValueError(f'{name} is an attribute for this product')
                for k, v in attr_names.items():
                    if k not in attributes:
                        raise ValueError(f'{k} is not an attribute for this product')
                    for attr in attrs.get('attributes'):
                        if k == attr.get('name'):
                            if attr.get('required') and attr_names.get(name) is None:
                                raise ValueError(f'{name} is required')
                            # if attr.get('required') is False and v is None:
                            #     v = attr.get('default_value')
                            if attr.get('values'):
                                if v not in attr.get('values'):
                                    raise ValueError(f'{v} is not in values')
                            if attr.get('input_type') == 'Price':
                                if type(v) != int:
                                    raise ValueError(f'{k} must be integer!')
                            # if attr.get('input_type') == 'Color':
                            #     if type(v) != int:
                            #         raise ValueError(f'{k} must be integer!')
                            if attr.get('input_type') == 'Dropdown':
                                if type(v) != int or v < len(attr.get('values')):
                                    raise ValueError(f'{k} must be integer!')
                            if attr.get('input_type') == 'Text Field':
                                if type(v) != str:
                                    raise ValueError(f'{k} must be string!')
                                if len(v) < 3:
                                    raise ValueError(f'{k} must be gth 3 character!')
                            if attr.get('input_type') == 'Text Area':
                                if type(v) != str:
                                    raise ValueError(f'{k} must be string!')
                                if len(v) < 3:
                                    raise ValueError(f'{k} must be gth 3 character!')
                            if attr.get('input_type') == 'Text Editor':
                                if type(v) != str:
                                    raise ValueError(f'{k} must be string!')
                                if len(v) < 3:
                                    raise ValueError(f'{k} must be gth 3 character!')
                            if attr.get('input_type') == 'Media Image':
                                if type(v) != str:
                                    raise ValueError(f'{k} must be string!')
                                if len(v) < 3:
                                    raise ValueError(f'{k} must be gth 3 character!')
                            if isinstance(attr.get('input_type'), datetime.date):
                                if type(v) != date:
                                    raise ValueError(f'{k} must be Date!')
                            if attr.get('input_type') == "Yes or No":
                                if type(v) != bool:
                                    raise ValueError(f'{k} must be Yes or No!')
                            if attr.get('input_type') == 'Multiple Select':
                                if type(v) != list:
                                    raise ValueError(f'{k} must be a list!')
                            if attr.get('input_type') == "Number":
                                if type(v) != (int or float):
                                    raise ValueError(f'{k} must be integer or flout!')
                            # input_type = ['Text Field', 'Text Area', 'Text Editor', 'Date', 'Date and Time',
                            #               'Yes or No',
                            #               'Multiple Select', 'Dropdown', 'Price', 'Media Image', 'Color', 'Number']

            return attr_names

# {
#   "images": "string",
#   "color": "string",
#   "color7": "string",
#   "color8": "string",
#   "color9": "string",
#   "price": "string",
#   "color10": "string",
#   "color12": "string",
#   "color18": "string",
#   "color19": "string",
#   "color20": "string",
#   "COLOR": "green",
#   "DATE": 26,
#   "NUMBER": 523,
#   "YESORNO": true,
#   "PRICE": 200
# }