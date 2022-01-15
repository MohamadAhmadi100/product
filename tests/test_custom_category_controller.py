from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_add_product_to_custom_category():
    response = client.post("/custom_category/product/" + '100104021006', json={
                "name": "atish bazi"
            })
    assert response.status_code == 201
    assert response.json() == {'message': 'product created successfully'}


def test_remove_product_from_custom_category():
    response = client.delete('/custom_category/' + 'atish bazi' + '/product/' + '120501002003')
    assert response.status_code == 200
    assert response.json() == {f'message': f'product removed from atish bazi successfully'}


def test_get_products_of_custom_category():
    response = client.get('/custom_category/' + 'atish bazi' + '/products/')
    assert response.status_code == 200
    assert response.json() == []


def test_get_custom_categories():
    response = client.get('/custom_categories/')
    assert response.status_code == 200
    assert response.json() == []


def test_update_product_from_custom_category():
    response = client.get('/custom_category/product/' + '120501002003' + '/update/')
    assert response.status_code == 201
    assert client.get('/custom_category/' + 'atish bazi' + '/product/' + '120501002003') == []

