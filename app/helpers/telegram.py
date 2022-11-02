import logging
import traceback
from time import strftime, localtime
from app.config import settings
import requests


def send_telegram_message(msg):
    req = f"{settings.TELEGRAM_REQUEST_URL}send-message"
    requests.post(req, json={
        "text": msg,
        "parse_mode": "html"
    })


def exception_handler():
    telegram_id = settings.TELEGRAM_ID.split(",")[0]

    now = strftime("%Y-%m-%d %H:%M", localtime())
    message = f'<b>{settings.APP_NAME} | {now}</b>\n\n<pre language="python">' \
              f'Failed with exception:\n{traceback.format_exc()}</pre>\n{telegram_id} 💩'
    logging.error(message)
    if not settings.DEBUG_MODE:
        send_telegram_message(message)


def admin_handler(data):
    telegram_ids = settings.TELEGRAM_ID
    id_list = []
    id_list.append(telegram_ids.split(",")[1])
    id_list.append(telegram_ids.split(",")[2])
    for id in id_list:
        now = strftime("%Y-%m-%d %H:%M", localtime())
        message = f'<b> {now}</b>\n\n<pre language="python">' \
                  f'please check new error about:\n{data}type</pre>\n{id} 🙏'
        logging.error(message)
        if not settings.DEBUG_MODE:
            send_telegram_message(message)

