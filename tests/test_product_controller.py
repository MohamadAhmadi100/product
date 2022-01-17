from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_add_product(delete_product):
    response = client.post("/api/v1/product/", json={
        "system_code": "100104021006",
        "attributes": {
            "image": "/src/default.jpg",
            "year": 2020
        }
    })
    assert response.status_code == 201
    assert response.json() == {'message': 'product created successfully'}


def test_get_all_products(create_and_delete_multiple_products):
    response = client.get("/api/v1/products/1")
    assert response.status_code == 200
    print(response.json())
    assert response.json() == [{'attributes': {'image': '/src/default.jpg', 'year': 2020},
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


def test_get_product_by_system_code(create_and_delete_product):
    response = client.get("/api/v1/product/" + "100104021006")
    assert response.status_code == 200
    assert response.json() == {'attributes': {'image': '/src/default.jpg', 'year': 2020},
                               'brand': 'Mobile Xiaomi',
                               'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                               'main_category': 'Device',
                               'model': 'Xiaomi Redmi 9c',
                               'sub_category': 'Mobile',
                               'system_code': '100104021006'}


def test_update_product(create_and_delete_product):
    response = client.put("/api/v1/product/" + "100104021006",
                          json={'attributes': {'image': '/src/default.jpg', 'year': 1988},
                                'brand': 'Mobile Xiaomi',
                                'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                                'main_category': 'Device',
                                'model': 'Xiaomi Redmi 9c',
                                'sub_category': 'Mobile',
                                'system_code': '100104021006'})
    assert response.status_code == 202
    assert response.json() == {'message': 'product updated successfully'}


def test_delete_attribute(create_product):
    response = client.delete("/api/v1/product/" + "100104021006")
    assert response.status_code == 200
    assert response.json() == {"message": "product deleted successfully"}
