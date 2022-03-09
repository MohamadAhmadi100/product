from app.listener import callback
from config import settings
from rabbit_client import RabbitRPCClient

if __name__ == '__main__':
    rpc = RabbitRPCClient(receiving_queue=f"{settings.APP_NAME}_rpc", callback=callback,
                          exchange_name="headers_exchange",
                          headers={settings.APP_NAME: True}, headers_match_all=True)
