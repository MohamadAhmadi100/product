from app.models.custom_category import CustomCategory


def test_add_product_to_custom_category():
    data = {
        "name": "atish bazi"
    }
    category = CustomCategory(**data)
    category.add_product_to_custom_category({'products': '100105015003'})
    print(category)
    assert category.get_products_from_custom_category() == []
