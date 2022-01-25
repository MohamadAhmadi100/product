from fastapi import Query, Path, HTTPException, APIRouter, Body

from app.models.product import CreateParent, CreateChild, AddAtributes, Product
from app.modules.attribute_setter import attribute_setter
from app.modules.kowsar_getter import KowsarGetter

router = APIRouter()


@router.get("/product/parent/", status_code=200)
def create_parent_schema():
    return CreateParent.schema().get("properties")


@router.post("/product/parent/", status_code=201)
def create_parent(
        item: CreateParent
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    if item.system_code_is_unique():
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=409, detail={"message": "product already exists", "label": "محصول موجود است",
                                                 "redirect": "/product/{system_code}"})


@router.get("/product/child/", status_code=200)
def create_child_schema():
    return CreateChild.schema().get("properties")


@router.post("/product/child/", status_code=201)
def create_child(
        item: CreateChild
) -> dict:
    """
    Create a product for sale in main collection in database.
    attributes will be validated before insert.
    """
    if item.system_code_is_unique():
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=409,
                        detail={"message": "product already exists", "label": "محصول موجود است",
                                "redirect": "/product/{system_code}"})


@router.get("/product/attributes/", status_code=200)
def add_attributes_schema():
    form = Product.schema().get("properties").copy()
    form["system_code"]["minLength"] = 12
    del form["name"]
    return form


@router.post("/product/attributes/", status_code=201)
def add_attributes(
        item: AddAtributes = Body(..., example={
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
    if not item.system_code_is_unique():
        item.validate_attributes()
        message, success = item.create()
        if success:
            return message
        raise HTTPException(status_code=417, detail=message)
    raise HTTPException(status_code=409,
                        detail={"message": "product doesn't exists", "label": "محصول موجود نیست",
                                "redirect": "/product/{system_code}"})


@router.get("/product/{system_code}", status_code=200)
def get_product_by_system_code(
        system_code: str = Path(..., min_length=9, max_length=9)
) -> dict:
    """
    Get a product by system_code in main collection in database.
    """
    result = Product.get_product_by_system_code(system_code)
    if result:
        return result
    raise HTTPException(status_code=404,
                        detail={"message": "product doesn't exists", "label": "محصول موجود نیست",
                                "redirect": "/product/{system_code}"})


@router.delete("/product/{system_code}", status_code=200)
def delete_product(
        system_code: str = Path(..., min_length=3, max_length=255)
) -> dict:
    """
    Delete a product by name in main collection in database.
    """
    product = CreateChild.construct()
    product.system_code = system_code
    if not product.system_code_is_unique():
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


@router.get("/product/{system_code}/items", status_code=200)
def suggest_product(system_code: str = Path(..., min_length=9, max_length=9)):
    data = KowsarGetter.system_code_items_getter(system_code)
    suggests = CreateChild.suggester(data, system_code)
    return suggests


@router.get("/categories/{system_code}/")
def get_all_categories(system_code: str = Path(00, min_length=2, max_length=6),
                       page: int = Query(1, ge=1, le=1000),
                       per_page: int = Query(15, ge=1, le=1000)):
    """
    """
    return Product.get_all_categories(system_code, page, per_page)


@router.get("/product/mock/")
def get_mock():
    return {
        "kowsar_system_code": "100102001",
        "system_code": "10010200101",
        "name": "ggg",
        "main_category": "Device",
        "sub_category": "Mobile",
        "brand": "Mobile Apple",
        "model": "iPhone 11",
        "routes": {
            "route": "Device",
            "label": "لوازم الکترونیک ",
            "children": {
                "route": "Mobile",
                "label": "موبایل",
                "children": {
                    "route": "Mobile Apple",
                    "label": "موبایل اپل ",
                }
            }
        },
        "related_products": [{"kowsar_system_code": "100102001",
                              "system_code": "10010200101",
                              "name": "ggg",
                              "colors": [{
                                  "value": "black",
                                  "type": "color"}, {
                                  "value": "black",
                                  "type": "color"}],
                              "price": {
                                  "regular": 60000000,
                                  "special": 50000000,
                              }}],
        "attributes": {
            "images": {
                "main_image": "url",
                "closeup_image": "url",
                "other_images": ["url", "url"]
            },
            "storage": {"attribute_label": "حافظه داخلی",
                        "label": "۶۴"},
            "ram": {"attribute_label": "رم",
                    "label": "۸"}
        },
        "visible_to_site": True,
        "products": [
            {
                "kowsar_system_code": "100102001001",
                "system_code": "10010200101001",
                "config": {
                    "color": {"attribute_label": "رنگ",
                              "value": "black",
                              "label": "مشکی",
                              "type": "color"},
                    "guarantee": {"attribute_label": "گارانتی",
                                  "value": "awat",
                                  "label": "آوات",
                                  "type": "radio"},
                    "seller": {"attribute_label": "فروشنده",
                               "value": "aasood",
                               "label": "آسود",
                               "type": "radio"},
                    "warehouse": [{"quantity": 0,
                                   "price": 0,
                                   "special_price": 0,
                                   "warehouse_id": 0,
                                   "warehouse_state": "",
                                   "warehouse_city": "",
                                   "warehouse_state_id": "",
                                   "warehouse_city_id": "",
                                   "warehouse_label": "تهران",
                                   "attribute_label": "انبار"},
                                  {"quantity": 0,
                                   "price": 0,
                                   "special_price": 0,
                                   "warehouse_id": 0,
                                   "warehouse_state": "",
                                   "warehouse_city": "",
                                   "warehouse_state_id": "",
                                   "warehouse_city_id": "",
                                   "warehouse_label": "مشهد",
                                   "attribute_label": "انبار"}]
                },
                "visible_to_site": True,
            },
            {
                "kowsar_system_code": "100102001002",
                "system_code": "10010200101002",
                "config": {
                    "color": {"attribute_label": "رنگ",
                              "value": "black",
                              "label": "مشکی",
                              "type": "color"},
                    "guarantee": {"attribute_label": "گارانتی",
                                  "value": "awat",
                                  "label": "آوات",
                                  "type": "radio"},
                    "seller": {"attribute_label": "فروشنده",
                               "value": "aasood",
                               "label": "آسود",
                               "type": "radio"},
                    "warehouse": [{"quantity": 0,
                                   "price": 0,
                                   "special_price": 0,
                                   "warehouse_id": 0,
                                   "warehouse_state": "",
                                   "warehouse_city": "",
                                   "warehouse_state_id": "",
                                   "warehouse_city_id": "",
                                   "warehouse_label": "تهران",
                                   "attribute_label": "انبار"},
                                  {"quantity": 0,
                                   "price": 0,
                                   "special_price": 0,
                                   "warehouse_id": 0,
                                   "warehouse_state": "",
                                   "warehouse_city": "",
                                   "warehouse_state_id": "",
                                   "warehouse_city_id": "",
                                   "warehouse_label": "مشهد",
                                   "attribute_label": "انبار"}]
                },
                "visible_to_site": True,
            }
        ]
    }
