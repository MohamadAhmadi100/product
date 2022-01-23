from app.modules.kowsar_getter import KowsarGetter
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/{system_code}/", status_code=200)
def get_kowsar(system_code: str):
    """
    Get kowsar data by full system_code(12 digits)
    """
    data = KowsarGetter.system_code_name_getter(system_code)
    if data:
        return data
    raise HTTPException(status_code=404,
                        detail={"message": "product doesn't exists", "label": "محصول موجود نیست",
                                "redirect": "/product/{system_code}"})


@router.get("/{system_code}/items/", status_code=200)
def get_kowsar_items(system_code: str):
    """
    Get sub categories of kowsar tree(2 to 9 digits)
    For the root category use "00"
    """
    data = KowsarGetter.system_code_items_getter(system_code)
    if data:
        return data
    raise HTTPException(status_code=404,
                        detail={"message": "product doesn't exists", "label": "محصول موجود نیست",
                                "redirect": "/product/{system_code}"})


@router.get("/update_collection", status_code=200)
def update_kowsar_collection():
    """
    update kowsar collection from kala file(.xls)
    """
    kowsar = KowsarGetter()
    kowsar.product_getter()
    kowsar.update_kowsar_collection()
    return {"message": "kowsar collection updated", "label": "جدول کالاهای کوثر بروز شد"}
