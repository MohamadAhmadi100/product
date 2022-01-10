from app.models.product import Product
from fastapi import Query, Path, HTTPException, APIRouter

router = APIRouter()


@router.post("/api/v1/product/", tags=["product"], status_code=201)
def add_product(
        item: Product
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    if item.system_code_is_unique():
        if item.validate_attributes():
            message, success = item.create()
            if success:
                return message
            raise HTTPException(status_code=417, detail=message)
        raise HTTPException(status_code=417, detail='attributes are not valid')
    raise HTTPException(status_code=409, detail="product already exists")


@router.get("/api/v1/products/{page}", tags=["product"], status_code=200)
def get_products(
        page: int = Path(1, ge=1, le=1000),
        per_page: int = Query(10, ge=1, le=1000)
) -> list:
    """
    Get all the products of the main collection in database.
    It shows 10 products per page.
    """
    product = Product.construct()
    return product.get(page=page, per_page=per_page)


@router.get("/api/v1/product/{system_code}", tags=["product"], status_code=200)
def get_product_by_system_code(
        system_code: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    product = Product.construct()
    stored_data = product.get(system_code)
    if stored_data:
        return stored_data
    raise HTTPException(status_code=404, detail="product not found")


@router.put("/api/v1/product/{system_code}", tags=["product"], status_code=202)
def update_product(
        item: Product,
        system_code: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Update a product by system_code in main collection in database.
    """
    product = Product.construct()
    stored_data = product.get(system_code=system_code)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_data.copy(update=update_data)
    if item.validate_attributes():
        message, success = item.update(updated_item.dict())
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=417, detail='attributes are not valid')


@router.delete("/api/v1/product/{system_code}", tags=["product"], status_code=200)
def delete_product(
        system_code: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Delete a product by name in main collection in database.
    """
    product = Product.construct()
    stored_data = product.get(system_code)
    if stored_data:
        message, success = product.delete()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=404, detail="product not found")
