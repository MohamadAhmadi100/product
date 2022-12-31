import sys

from config import settings

# Important imports dont remove
from app.controllers.product_controller import *
from app.controllers.kowsar_controller import *
from app.controllers.attributes_controller import *
from app.controllers.custom_category import *
from app.controllers.change_qty_reserve_controller import *
from app.controllers.checkout_controller import *
from app.controllers.scm_controller import *
from app.controllers.order import *
from app.controllers.warehouse_controller import *
from app.controllers.reports import *

from app.modules import terminal_log

response = {}
app_name = settings.APP_NAME


def callback(message: dict) -> dict:
    terminal_log.action_log(message, app_name)
    terminal_log.request_log(message, app_name)
    data = message.get(app_name, {})
    action = data.get("action")
    if action:
        body = data.get("body", {})
        try:
            exec(f"global response; response['{app_name}'] = {action}(**{body})")
            return response
        except Exception as e:
            return {f"{app_name}": {"success": False, "status_code": 503, "error": f"{app_name}: {e}"}}
    else:
        return {f"{app_name}": {"success": False, "status_code": 501, "error": f"{app_name}: action not found"}}
