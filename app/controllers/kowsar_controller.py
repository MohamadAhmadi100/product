from fastapi import Query, Path, HTTPException, APIRouter, Body

from app.module.kowsar_getter import KowsarGetter

router = APIRouter()


@router.get("/api/v1/kowsar/{system_code}", tags=["kowsar"], status_code=200)
def get_kowsar(system_code: str):
    data = KowsarGetter.system_code_name_getter(system_code)
    return data


@router.get("/api/v1/kowsar/items/{system_code}", tags=["kowsar"], status_code=200)
def get_kowsar_items(system_code: str):
    data = KowsarGetter.system_code_items_getter(system_code)
    return data