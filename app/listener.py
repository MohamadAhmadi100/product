import sys

from config import settings

# Important imports dont remove
from app.controllers.product_controller import *
from app.controllers.kowsar_controller import *

response = {}
app_name = settings.APP_NAME


def callback(message: dict) -> dict:
    sys.stdout.write("\033[1;31m")
    print("\n => Entry action: ", end="")
    sys.stdout.write("\033[;1m\033[1;34m")
    print(message.get(app_name).get("action"))
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
