from app.modules.attributes_modules import AttributesModules


def update_attributes(attributes: dict):
    result, created = AttributesModules.attribute_setter(attributes)
    if result:
        if created:
            return {"message": "Attributes created successfully", "status": 201, "success": True}
        return {"message": "Attributes updated successfully", "status_code": 202, "success": True}
    return {"message": "Attributes not created", "status_code": 400, "success": False}


def delete_attributes(name: str):
    result = AttributesModules.delete_attribute(name)

    if result:
        return {"message": "Attributes deleted successfully", "status_code": 202, "success": True}
    return {"message": "Attributes not deleted", "status_code": 400, "success": False}
