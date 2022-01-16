from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_main_page(create_and_delete_multiple_products):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == [{'attributes': {},
                                'brand': 'Tablet Lenovo',
                                'config': {'color': 'black', 'guarantee': 'sherkati', 'storage': '16'},
                                'main_category': 'Device',
                                'model': 'M7',
                                'sub_category': 'Tablet',
                                'system_code': '100201002002'}]


def test_add_product(delete_product):
    response = client.post("/api/v1/product/", json={})
    assert response.status_code == 201
    assert response.json() == {'message': 'product created successfully'}


def test_get_attributes(create_and_delete_multiple_products):
    response = client.get("/api/v1/product/1")
    assert response.status_code == 200
    assert response.json() == []


def test_get_attribute_by_name(create_and_delete_product):
    response = client.get("/api/v1/product/" + "120301001001")
    assert response.status_code == 200
    assert response.json() == {}


def test_update_attribute(create_and_delete_product):
    response = client.put("/api/v1/product/" + "120301001001",
                          json={})
    assert response.status_code == 202
    assert response.json() == {'message': 'product updated successfully'}


def test_delete_attribute(create_product):
    response = client.delete("/api/v1/product/" + "120301001001")
    assert response.status_code == 200
    assert response.json() == {"message": "product deleted successfully"}
