from fastapi import Query, Path, HTTPException, APIRouter, Body

from app.models.product import Product, Assignees

router = APIRouter()


@router.post("/api/v1/product/", tags=["product API"], status_code=201)
def add_product(
        item: Product
) -> dict:
    """
    Add an attribute to main collection in database with this information:
    - **name**: name of the attribute(for searching)
    - **label**: label of the attribute(for display)
    - **input_type**: type of input for the attribute
        - It will be index number of these things: ['Text Field', 'Text Area', 'Text Editor', 'Date', 'Date and Time',
        'Yes or No', 'Multiple Select', 'Dropdown', 'Price', 'Media Image', 'Color', 'Number']
    - **required**: if the attribute is required or not(Boolean type)
    - **use_in_filter**: if the attribute is used in filter or not(Boolean type)
    - **use_for_sort**: if the attribute is used for sorting or not(Boolean type)
    - **parent**: declare parent attribute to set attribute to it's children
    - **default_value**: default value of the attribute
    - **values**: list of values for the attribute
    - **set_to_nodes**: if the attribute is set to nodes or not(Boolean type)
    """
    if item.system_code_is_unique():
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=409, detail="product already exists")


@router.get("/api/v1/product/{page}", tags=["product API"], status_code=200)
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


@router.get("/api/v1/product/{system_code}", tags=["product API"], status_code=200)
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


@router.put("/api/v1/product/{system_code}", tags=["product API"], status_code=202)
def update_product(
        item: Product,
        system_code: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Update a product by system_code in main collection in database.
    """
    attribute = Product.construct()
    stored_data = attribute.get(system_code)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_data.copy(update=update_data)
    message, success = item.update(updated_item.dict())
    if success:
        return message
    raise HTTPException(status_code=417, detail=message)


@router.delete("/api/v1/product/{system_code}", tags=["product API"], status_code=200)
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


@router.get("/api/v1/attribute_by_kowsar/", tags=["attribute"], status_code=200)
def update_product_by_set_to_nodes():
    result = Assignees.set_all_attributes_by_set_to_nodes()
    if result:
        return {'status': 'success'}
    return {'error': 'update attribute failed'}


@router.get("/api/v1/attributes/", tags=["attribute"], status_code=200)
def get_all_attributes():
    result = Assignees.get_all_attributes_from_attribute_api()
    return {'result': result}


@router.get("/api/v1/attributes/{system_code}", tags=["attribute"], status_code=200)
def get_all_attribute_by_system_code(system_code: str):
    return Assignees.get_all_attribute_by_system_code(system_code=system_code)