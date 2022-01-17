from app.models.product import Product


def test_add_product(delete_product):
    sample_data = {
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    }
    product = Product(**sample_data)
    product.create()
    print(product.get('100104021006'))
    assert product.get("100104021006") == Product(system_code='100104021006', main_category='Device',
                                                  sub_category='Mobile', brand='Mobile Xiaomi', model='Xiaomi Redmi 9c',
                                                  config={'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                                                  attributes={'image': '/src/default.jpg', 'year': 2020})


def test_get_product(create_and_delete_product):
    product = Product.construct()
    assert product.get("100104021006") == Product(main_category='Device', sub_category='Mobile', brand='Mobile Xiaomi',
                                                  model='Xiaomi Redmi 9c',
                                                  config={'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                                                  attributes={'image': '/src/default.jpg', 'year': 2020},
                                                  system_code='100104021006')


def test_get_all_products(create_and_delete_multiple_products):
    product = Product.construct()
    assert product.get() == [{'attributes': {'image': '/src/default.jpg', 'year': 2020},
                              'brand': 'Tablet Lenovo',
                              'config': {'color': 'black', 'guarantee': 'sherkati', 'storage': '16'},
                              'main_category': 'Device',
                              'model': 'M7',
                              'sub_category': 'Tablet',
                              'system_code': '100201002002'},
                             {'attributes': {'image': '/src/default.jpg', 'year': 2020},
                              'brand': 'Mobile Sumsung',
                              'config': {'color': 'white',
                                         'guarantee': 'sherkati',
                                         'ram': '2gb',
                                         'storage': '32gb'},
                              'main_category': 'Device',
                              'model': 'M01 Core',
                              'sub_category': 'Mobile',
                              'system_code': '100101047003'},
                             {'attributes': {'image': '/src/default.jpg', 'year': 2020},
                              'brand': 'Mobile Xiaomi',
                              'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                              'main_category': 'Device',
                              'model': 'Xiaomi Redmi 9c',
                              'sub_category': 'Mobile',
                              'system_code': '100104021006'}]


def test_update_product(create_and_delete_product):
    product = Product.construct()
    product = product.get("100104021006")
    updated_data = {'attributes': {'image': '/src/default.jpg', 'year': 1988},
                    'brand': 'Mobile Xiaomi',
                    'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                    'main_category': 'Device',
                    'model': 'Xiaomi Redmi 9c',
                    'sub_category': 'Mobile',
                    'system_code': '100104021006'}
    product.update(updated_data)
    assert product.get("100104021006") == Product(main_category='Device', sub_category='Mobile', brand='Mobile Xiaomi',
                                                  model='Xiaomi Redmi 9c',
                                                  config={'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                                                  attributes={'image': '/src/default.jpg', 'year': 1988},
                                                  system_code='100104021006')


def test_delete_product(create_product):
    product = Product.construct()
    product.get("100104021006")
    product.delete()
