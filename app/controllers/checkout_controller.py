from app.models.product import Quantity


def get_quantity_list(item: dict) -> dict:
    result = Quantity.get_quantity_list(item)
    if result:
        return {"success": True, "status_code": 200, "message": result}
    return {"success": False, "status_code": 404, "error": "quantity not found"}
