from product.database.models import Product


def test_create_product(create_and_delete_product_fixture):
    assert create_and_delete_product_fixture.get_product(system_code='100101030001') is not None
    assert type(create_and_delete_product_fixture.get_product(system_code='100101030001')) == dict
    sample_product = create_and_delete_product_fixture.get_product(system_code='100101030001')
    assert sample_product == {'system_code': '100101030001',
                              'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'},
                              'model': 'A022', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile',
                              'main_category': 'Device', 'image': 'src/default.png'}


def test_delete_product(create_product_fixture):
    create_product_fixture.delete_product(system_code='100101030001')
    assert create_product_fixture.get_product(system_code='100101030001') is None


def test_get_product(create_and_delete_product_fixture):
    data = create_and_delete_product_fixture.get_product(system_code='100101030001')
    assert type(data) == dict
    assert data == {'system_code': '100101030001',
                    'config': {'storage': '64gb', 'color': 'black', 'guarantee': 'sherkati', 'ram': '3gb'},
                    'model': 'A022', 'brand': 'Mobile Sumsung', 'sub_category': 'Mobile', 'main_category': 'Device',
                    'image': 'src/default.png'}


def test_get_all_products(create_and_delete_products_fixture):
    data = create_and_delete_products_fixture.get_all_products(page=1, product_count=3)
    print(data)
    assert type(data) == list
    assert len(data) == 3
    assert type(data[0]) == dict
    sample_data = [
        {'system_code': '120301001001', 'config': {'color': 'color', 'guarantee': 'life time', 'storage': '8'},
         'model': 'Cruzer blade cz50', 'brand': 'Flash Memory SanDisk', 'sub_category': 'Flash Memory',
         'main_category': 'Accessory', 'images': 'dddddd', 'country': 'iran'},
        {'system_code': '120301004002', 'config': {'color': 'color', 'guarantee': 'life time', 'storage': '128'},
         'model': 'Ultra Trek CZ490', 'brand': 'Flash Memory SanDisk', 'sub_category': 'Flash Memory',
         'main_category': 'Accessory', 'images': 100},
        {'system_code': '120501002003', 'config': {'color': 'white', 'guarantee': 'nog', 'capacity': '20k'},
         'model': 'All Xiaomi Redm PowerBank', 'brand': 'PowerBank Xiaomi', 'sub_category': 'PowerBank',
         'main_category': 'Accessory', 'images': 'abcd'}]

    for i in range(0, 3):
        assert data[i] == sample_data[i]


def test_update_product(create_and_delete_product_fixture):
    data = {'system_code': '100101030001',
            'image': 'Myimage'}
    assert Product.update_product("100101030001", data).get("messages") == "product updated"
