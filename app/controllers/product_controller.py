from fastapi import Query, Path, HTTPException, APIRouter

from app.models.product import Product
from app.modules.attribute_setter import attribute_setter
from app.modules.kowsar_getter import KowsarGetter

router = APIRouter()


# @router.post("/product/", status_code=201)
# def create_product(
#         item: Product
# ) -> dict:
#     """
#     Create a product for sale in main collection in database.
#     attributes will be validated before insert.
#     """
#     if item.system_code_is_unique():
#         message, success = item.create()
#         if success:
#             return message
#         raise HTTPException(status_code=417, detail=message)
#     raise HTTPException(status_code=409, detail="product already exists")


####


@router.post("/product/parent/", status_code=201)
def create_parent(
        item: Product
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    if item.system_code_is_unique():
        item.step = 1
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=409, detail="product already exists")


@router.post("/product/child/", status_code=201)
def create_child(
        item: Product
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    if item.system_code_is_unique():
        item.step = 2
        if not item.check_parent():
            raise HTTPException(status_code=409, detail="product parent doesn't exist")
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=409, detail="product already exists")


@router.post("/product/attributes/", status_code=201)
def add_attributes(
        item: Product
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    item.step = 3
    if not item.check_parent():
        raise HTTPException(status_code=409, detail="product parent doesn't exist")
    message, success = item.add_attributes()
    if success:
        return message
    raise HTTPException(status_code=417, detail=message)


# @router.post("/product/", status_code=201)
# def add_product(
#         item: Product
# ) -> dict:
#     """
#     Create a product for sale in main collection in database.
#     attributes will be validated before insert.
#     """
#     if item.system_code_is_unique():
#         item.validate_attributes()
#         message, success = item.create()
#         if success:
#             return message
#         raise HTTPException(status_code=417, detail=message)
#     raise HTTPException(status_code=409, detail="product already exists")


@router.get("/products/{page}", status_code=200)
def get_all_products(
        page: int = Path(1, ge=1, le=1000),
        per_page: int = Query(10, ge=1, le=1000)
) -> list:
    """
    Get all the products of the main collection in database.
    It shows 10 products per page.
    """
    product = Product.construct()
    return product.get(page=page, per_page=per_page)


@router.get("/product/{system_code}", status_code=200)
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


# @router.put("/product/", status_code=202)
# def update_product(
#         item: Product,
# ) -> dict:
#     """
#     Update a product by system_code in main collection in database.
#     """
#     if item.step == 2:
#         if item.system_code_is_unique():
#             message, success = item.create()
#             if success:
#                 return message
#             raise HTTPException(status_code=417, detail=message)
#         raise HTTPException(status_code=409, detail="product already exists")
#     elif item.step == 3:
#         product = Product.construct()
#         stored_data = product.get(system_code=item.system_code)
#         stored_data.step += 1
#         if not stored_data:
#             raise HTTPException(status_code=417, detail="product is not exist")
#         stored_data.attributes = item.attributes
#         item.validate_attributes()
#         message, success = item.update(stored_data.dict())
#         if success:
#             return message
#         raise HTTPException(status_code=417, detail=message)
#     else:
#         raise HTTPException(status_code=409, detail="invalid step")

# if item.system_code_is_unique():
#     product = Product.construct()
#     system_code = item.system_code
#
#     stored_data = product.get(system_code=item.system_code)
#     if item.step == 3:
#         item.validate_attributes()
#         if stored_data.dict().get('step') + 1 != item.step:  # TODO ask Q
#             raise HTTPException(status_code=417, detail={"error": "product step is invalid"})
#         update_data = item.dict(exclude_unset=True)
#         updated_item = stored_data.copy(update=update_data)
#         message, success = item.update(updated_item.dict(), stored_data.dict().get('system_code'))
#         if success:
#             return message
#         raise HTTPException(status_code=417, detail=message)
#     elif item.step == 2:
#         item.attributes = {}
#         item.name = stored_data.dict().get('name')
#         message, success = item.create()
#         if success:
#             return message
#     raise HTTPException(status_code=409, detail="product already exists")
# raise HTTPException(status_code=409, detail="product already exists")


# @router.put("/product/{system_code}", status_code=202)
# def update_product(
#         item: Product,
#         system_code: str = Path(..., min_length=3, max_length=255)
# ) -> dict:
#     """
#     Update a product by system_code in main collection in database.
#     """
#     if item.system_code != system_code:
#         raise HTTPException(status_code=400, detail="system_code is not valid")
#     product = Product.construct()
#     stored_data = product.get(system_code=system_code)
#     update_data = item.dict(exclude_unset=True)
#     updated_item = stored_data.copy(update=update_data)
#     item.validate_attributes()
#     message, success = item.update(updated_item.dict())
#     if success:
#         return message
#     raise HTTPException(status_code=417, detail=message)


@router.delete("/product/{system_code}", status_code=200)
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


@router.get("/product/update_attribute_collection/", status_code=200)
def update_attribute_collection():
    """
    Update the attribute collection in database.
    """
    # TODO: Later, the attributes below should come from API GW
    attributes = [
        {
            "required": True,
            "use_in_filter": False,
            "use_for_sort": False,
            "default_value": None,
            "values": None,
            "set_to_nodes": False,
            "name": "year",
            "label": "رنگ",
            "input_type": "Number",
            "parent": "100104021006"
        },
        {
            "required": False,
            "use_in_filter": False,
            "use_for_sort": False,
            "default_value": "/src/default.png",
            "values": None,
            "set_to_nodes": True,
            "name": "image",
            "label": "عکس",
            "input_type": "Media Image",
            "parent": "1001"
        }
    ]
    attribute_setter(attributes)
    return {"message": "success"}


@router.get("/product/suggest/{system_code}", status_code=200)
def suggest_product(system_code: str = Path(..., min_length=9, max_length=9)):
    data = KowsarGetter.system_code_items_getter(system_code)
    suggests = Product.suggester(data)
    return suggests
