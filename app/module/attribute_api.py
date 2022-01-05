import requests
import json


class Attribute:
    @staticmethod
    def get_all_attributes_by_assignee():
        url = 'http://127.0.0.1:8001/assignee/' + 'product' + '/attrs/'
        response = requests.get(url).json()
        return response


