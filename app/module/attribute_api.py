import requests
import json


class Attribute:
    @staticmethod
    def get_all_attributes_by_assignee():
        url = 'http://0.0.0.0:3000/api/v1/assignee/' + 'product' + '/attrs/'
        response = requests.get(url).json()
        return response


