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
    now = strftime("%Y-%m-%d %H:%M", localtime())
    message = f'<b>{settings.APP_NAME} | {now}</b>\n\n<pre language="python">' \
              f'Failed with exception:\n{traceback.format_exc()}</pre>\n{settings.TELEGRAM_ID} 💩'
    logging.error(message)
    if not settings.DEBUG_MODE:
        send_telegram_message(message)


def admin_handler(data):
    x = settings.TELEGRAM_ID
    s = []
    s.append(x.split(",")[1])
    s.append(x.split(",")[0])
    for id in s:
        now = strftime("%Y-%m-%d %H:%M", localtime())
        message = f'<b> {now}</b>\n\n<pre language="python">' \
                  f'please check new error about:\n{data} type</pre>\n{id} 🙏'
        logging.error(message)
        if not settings.DEBUG_MODE:
            send_telegram_message(message)
