from fastapi import Query, Path, HTTPException, APIRouter, Body

from app.models.product import Product, Child
from app.modules.attribute_setter import attribute_setter
from app.modules.kowsar_getter import KowsarGetter

router = APIRouter()


@router.get("/product/parent/", status_code=200)
def create_parent():
    form = Product.schema().get("properties").copy()
    del form["attributes"]
    form["system_code"]["maxLength"] = 9
    return form


@router.post("/product/parent/", status_code=201)
def create_parent(
        item: Product = Body(..., example={
            "system_code": "100104021",
            "name": "ردمی 9c"
        })
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    if item.system_code_is_unique():
        item.step_setter(1)
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=409, detail={"message": "product already exists", "label": "محصول موجود است",
                                                 "redirect": "/product/{system_code}"})


@router.get("/product/child/", status_code=200)
def create_child():
    form = Product.schema().get("properties").copy()
    form["system_code"]["minLength"] = 12
    del form["name"]
    del form["attributes"]
    return form


@router.post("/product/child/", status_code=201)
def create_child(
        item: Child = Body(..., example={
            "system_codes": ["100104021006"]
        })
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    system_codes = item.system_codes
    item = Product.construct()
    item.step_setter(2)
    for system_code in system_codes:
        item.system_code = system_code
        if not item.system_code_is_unique():
            raise HTTPException(status_code=409,
                                detail={"message": "product already exists", "label": "محصول موجود است",
                                        "redirect": "/product/{system_code}"})
        if not item.check_parent():
            raise HTTPException(status_code=409,
                                detail={"message": "product parent doesn't exist", "label": "محصول والد موجود نیست",
                                        "redirect": "/product/parent/"})
    message, success = item.create_child(system_codes)
    if success:
        return message
    raise HTTPException(status_code=417, detail=message)


@router.get("/product/attributes/", status_code=200)
def add_attributes():
    form = Product.schema().get("properties").copy()
    form["system_code"]["minLength"] = 12
    del form["name"]
    return form


@router.post("/product/attributes/", status_code=201)
def add_attributes(
        item: Product = Body(..., example={
            "system_code": "100104021006",
            "attributes": {
                "image": "/src/default.jpg",
                "year": 2020
            }
        })
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    item.step_setter(3)
    if not item.check_parent():
        raise HTTPException(status_code=409,
                            detail={"message": "product parent doesn't exist", "label": "محصول والد موجود نیست",
                                    "redirect": "/product/child/"})
    item.validate_attributes()
    message, success = item.add_attributes()
    if success:
        return message
    raise HTTPException(status_code=417, detail=message)


@router.get("/products/{page}", status_code=200)
def get_all_products(
        page: int = Path(1, ge=1, le=1000),
        per_page: int = Query(10, ge=1, le=1000)
) -> dict:
    """
    Get all the products of the main collection in database.
    It shows 10 products per page.
    """
    product = Product.construct()
    headers, data = product.get(page=page, per_page=per_page)
    return {"headers": headers, "data": data}


@router.get("/product/{system_code}", status_code=200)
def get_product_by_system_code(
        system_code: str = Path(..., min_length=9, max_length=9)
) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    product = Product.construct()
    stored_data = product.get(system_code)
    output = dict()
    for data in stored_data:
        if stored_data.index(data) == 0:
            output.update(data)
            output.update({"products": list()})
            continue
        output['products'].append(data)
    if stored_data:
        return output
    raise HTTPException(status_code=404, detail={"message": "product not found", "label": "محصول یافت نشد"})


@router.delete("/product/{system_code}", status_code=200)
def delete_product(
        system_code: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Delete a product by name in main collection in database.
    """
    product = Product.construct()
    stored_data = product.get_object(system_code)
    if stored_data:
        message, success = product.delete()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=404, detail={"message": "product not found", "label": "محصول یافت نشد"})


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
            "label": "سال",
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
    return {"message": "attribute collection updated", "label": "جدول تنظیمات بروز شد"}


@router.get("/product/suggest/{system_code}", status_code=200)
def suggest_product(system_code: str = Path(..., min_length=9, max_length=9)):
    data = KowsarGetter.system_code_items_getter(system_code)
    suggests = Product.suggester(data)
    return suggests
