from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_add_product_to_custom_category(delete_product_from_custom_category):
    response = client.post("/api/v1/custom_category/product/" + '100104021006', json={
        "name": "atish bazi"
    })
    assert response.status_code == 201
    assert response.json() == {'message': 'product assigned to atish bazi successfully'}


def test_remove_product_from_custom_category(add_product_to_custom_category):
    response = client.delete('/api/v1/custom_category/' + 'atish bazi' + '/product/' + '100104021006')
    assert response.status_code == 200
    assert response.json() == {f'message': f'product removed from atish bazi successfully'}


def test_get_products_of_custom_category(add_and_remove_product_from_category):
    response = client.get('/api/v1/custom_category/' + 'atish bazi' + '/products/')
    assert response.status_code == 200
    assert response.json() == [{'attributes': {'image': '/src/default.jpg', 'year': 2020},
                                 'brand': 'Mobile Xiaomi',
                                 'config': {'color': 'orange', 'guarantee': 'sherkati', 'storage': '64'},
                                 'main_category': 'Device',
                                 'model': 'Xiaomi Redmi 9c',
                                 'sub_category': 'Mobile',
                                 'system_code': '100104021006'}]


def test_get_custom_categories():
    response = client.get('/api/v1/custom_categories/')
    assert response.status_code == 200
    assert response.json() == ['atish bazi']


def test_update_product_from_custom_category(add_and_remove_product_from_category):
    response = client.post('/api/v1/custom_category/product/' + '100104021006' + '/update/', json={
        "name": "atish bazi"
    })
    assert response.status_code == 201
    assert response.json() == {'message': 'product updated successfully'}
