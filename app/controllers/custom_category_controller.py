from app.models.custom_category import CustomCategory
from app.models.product import Product
from fastapi import Path, HTTPException, APIRouter

router = APIRouter()


@router.post("/custom_category/product/{system_code}", status_code=201)
def add_product_to_custom_category(
        item: CustomCategory,
        system_code: str = Path(..., min_length=2, max_length=12)
) -> dict:
    """
    Add a product to custom category collection in database.
    """
    product = Product.construct()
    product.get(system_code)
    if product:
        message, success = item.add_product_to_custom_category(product.dict())
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=404, detail="Product not found")


@router.delete("/custom_category/{custom_category}/product/{system_code}", status_code=200)
def remove_product_from_custom_category(
        custom_category: str = Path(..., min_length=3, max_length=128),
        system_code: str = Path(..., min_length=2, max_length=12)
) -> dict:
    """
    Remove a product from custom category collection in database.
    """
    product = Product.construct()
    stored_data = product.get(system_code)
    if stored_data:
        c_cat = CustomCategory(name=custom_category)
        message, success = c_cat.remove_product_from_custom_category(stored_data.dict())
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=404, detail={"error": "product not found"})


@router.get("/custom_category/{custom_category}/products/", status_code=200)
def get_products_of_custom_category(
        custom_category: str = Path(..., min_length=3, max_length=128)
) -> list:
    """
    Get all products of a custom category.
    """
    c_cat = CustomCategory(name=custom_category)
    products = c_cat.get_products_from_custom_category()
    if products:
        return products
    raise HTTPException(status_code=404, detail={"error": "products not found"})


@router.get("/custom_categories/", status_code=200)
def get_custom_categories() -> list:
    """
    Get all the name of custom categories.
    """
    custom_category = CustomCategory.construct()
    return custom_category.get_custom_categories()


@router.post("/custom_category/product/{system_code}/update/", status_code=201)
def update_product_from_custom_category(
        item: CustomCategory,
        system_code: str = Path(..., min_length=2, max_length=12)
) -> dict:
    """
    Update a product from custom category collection in database.
    It gets updated version of product from product collection.
    """
    product = Product.construct()
    product.get(system_code)
    if product:
        message, success = item.update_product_from_custom_category(product.dict())
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=404, detail="Product not found")
