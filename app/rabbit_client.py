import json
import sys

import pika
from app.modules import terminal_log
from config import settings


class RabbitRPCClient:
    def __init__(
            self,
            receiving_queue: str,
            callback: callable,
            exchange_name: str,
            headers: dict,
            headers_match_all: bool = False
    ):
        self.host = settings.RABBIT_HOST
        self.port = settings.RABBIT_PORT
        self.user = settings.RABBIT_USER
        self.password = settings.RABBIT_PASS
        self.exchange_name = exchange_name
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.connect()
        self.receiving_queue = receiving_queue
        self.channel.queue_declare(queue=self.receiving_queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.callback = callback
        self.fanout_callback = None
        self.headers = headers
        if headers_match_all:
            self.headers["x-match"] = "all"
        else:
            self.headers["x-match"] = "any"
        self.channel.queue_bind(
            exchange=exchange_name,
            queue=self.receiving_queue,
            routing_key="",
            arguments=self.headers
        )
        self.consume()

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=self.credentials,
                # blocked_connection_timeout=86400  # 86400 seconds = 24 hours
            )
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='headers')
        self.channel.basic_qos(prefetch_count=1)
        
    def publish(self, channel, method, properties, body):
        message = self.callback(json.loads(body))
        terminal_log.responce_log(message)
        channel.basic_publish(exchange='',
                            routing_key=properties.reply_to,
                            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                            body=json.dumps(message))
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def fanout_callback_runnable(self, channel, method, properties, body):
        self.fanout_callback(json.loads(body))

    def fanout_callback_setter(self, fanout_callback):
        self.fanout_callback = fanout_callback

    def fanout_consume(self, exchange_name: str):
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        received_queue = self.channel.queue_declare(queue='', exclusive=True)
        received_queue_name = received_queue.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=received_queue_name)
        self.channel.basic_consume(
            queue=received_queue_name,
            on_message_callback=self.fanout_callback_runnable,
            auto_ack=True
        )
        self.channel.start_consuming()

    def consume(self):
        self.channel.basic_consume(queue=self.receiving_queue, on_message_callback=self.publish)
        try:
            terminal_log.connection_log(self.host, self.port, self.headers)
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
