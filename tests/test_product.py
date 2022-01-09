from app.models.product import Product


def test_add_product(delete_product):
    sample_data = {
        "system_code": "120301001001",
        "specification": {
            "country": "iran"
        }
    }
    product = Product(**sample_data)
    product.create()
    assert product.get("120301001001") == {
        "system_code": "120301001001",
        "specification": {
            "country": "iran"
        }
    }


def test_get_product(create_and_delete_product):
    product = Product.construct()
    assert product.get("120301001001") == {"system_code": "120301001001",
        "specification": {
            "country": "iran"
        }}


def test_get_products(create_and_delete_multiple_products):
    product = Product.construct()
    assert product.get() == [
    ]


def test_update_product(create_and_delete_product):
    product = Product.construct()
    product = product.get("120301001001")
    product.update()
    assert product.get("120301001001") == {}


def test_delete_product(create_product):
    product = Product.construct()
    product = product.get("120301001001")
    product.delete()
