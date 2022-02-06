import json
import sys

import pika

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
        self.port = 5672
        self.user = "rbtmq"
        self.password = "DeVrab!t123"
        self.connection = self.connect()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type="headers")
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

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                blocked_connection_timeout=86400  # 86400 seconds = 24 hours
            )
        )
        return connection

    def publish(self, channel, method, properties, body):
        message = self.callback(json.loads(body))
        sys.stdout.write("\033[1;31m")
        print("                  Responce: ", end="")
        sys.stdout.write("\033[;1m\033[1;34m")
        print(message)
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
            sys.stdout.write("\033[0;32m")
            print(" [x] Consumer running on host \"" + self.host + ":" + str(self.port) + "\" , "
                  + "headers : " + str(self.headers), end="")
            sys.stdout.write("\033[1;36m")
            print(" -- Waiting for Requests ...")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
