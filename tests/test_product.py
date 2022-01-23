from app.models.product import Product, CreateChild, CreateParent, AddAtributes
from tests.conftest import delete_parent


def test_add_parent():
    sample_data = {
        "system_code": "100104021",
        "name": "ردمی 9c"
    }
    product = CreateParent(**sample_data)
    product.create()
    assert product.get('100104021') == [{'brand': 'Mobile Xiaomi',
                                         'main_category': 'Device',
                                         'model': 'Xiaomi Redmi 9c',
                                         'name': 'ردمی 9c',
                                         'sub_category': 'Mobile',
                                         'system_code': '100104021'}]
    delete_parent()


def test_delete_parent(create_child):
    product = CreateParent.construct()
    product.get('100104021')
    product.delete()
    assert Product.get('100104021') == []


def test_create_child(create_parent):
    sample_data = {
        "system_code": "100104021006"
    }
    product = CreateChild(**sample_data)
    product.create()
    assert product.get("100104021") == [{'brand': 'Mobile Xiaomi',
                                         'main_category': 'Device',
                                         'model': 'Xiaomi Redmi 9c',
                                         'name': 'ردمی 9c',
                                         'products': [{'config': {'color': 'orange',
                                                                  'guarantee': 'sherkati',
                                                                  'storage': '64'},
                                                       'system_code': '100104021006'}],
                                         'sub_category': 'Mobile',
                                         'system_code': '100104021'}]
    delete_parent()


def test_delete_child(create_child):
    pass


def test_add_attribute(create_child):
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = AddAtributes(**sample_data)
    product.create()
    assert product.get('100104021') == [{'brand': 'Mobile Xiaomi',
                                         'main_category': 'Device',
                                         'model': 'Xiaomi Redmi 9c',
                                         'name': 'ردمی 9c',
                                         'products': [{'attributes': {'image': '/src/default.jpg', 'year': 2020},
                                                       'config': {'color': 'orange',
                                                                  'guarantee': 'sherkati',
                                                                  'storage': '64'},
                                                       'system_code': '100104021006'}],
                                         'sub_category': 'Mobile',
                                         'system_code': '100104021'}]
    delete_parent()


def test_delete_attribute(add_attributes):
    pass


def test_get_parent(create_child):
    product = CreateParent.construct()
    assert product.get() == ({'page': 1, 'per_page': 10, 'total_counts': 1},
                             [{'brand': 'Mobile Xiaomi',
                               'main_category': 'Device',
                               'model': 'Xiaomi Redmi 9c',
                               'name': 'ردمی 9c',
                               'products': [{'config': {'color': 'orange',
                                                        'guarantee': 'sherkati',
                                                        'storage': '64'},
                                             'system_code': '100104021006'}],
                               'sub_category': 'Mobile',
                               'system_code': '100104021'}])
    delete_parent()



