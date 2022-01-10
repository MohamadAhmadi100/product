import traceback
from time import strftime

from config import settings


def telegram_message_sender(message: str, timeout: int = 10):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    for chat_id in settings.CHAT_IDS:
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = {"chat_id": chat_id, "text": message}
        # requests.post(url, data=data, proxies={"https": "155.138.150.199:23456"}, timeout=timeout)
        requests.post(url, data=datas, timeout=timeout)


def fastapi_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            now = strftime("%Y-%m-%d %H:%M", localtime())
            message = f'{func.__name__} failed in {settings.APP_NAME} with exception:\n{traceback.format_exc()}'
            print(message)
            logging.error(message)
            try:
                telegram_message_sender(now + ": " + message)
            except Exception as e:
                print("Could not send message to Telegram:", e)

    return wrapper


def exception_handler(func):
    try:
        return func
    except Exception:
        now = strftime("%Y-%m-%d %H:%M", localtime())
        message = f'{func.__name__} failed in {settings.APP_NAME} with exception:\n{traceback.format_exc()}'
        print(message)
        logging.error(message)
        try:
            telegram_message_sender(now + ": " + message)
        except Exception as e:
            print("Could not send message to Telegram:", e)
