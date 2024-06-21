import pika
import logging
from utils.logger import get_logger
from typing import Optional

logger = get_logger()

# Set Pika logging level to WARNING to reduce verbosity
logging.getLogger('pika').setLevel(logging.WARNING)

class AMQ:
    def __init__(self, service_queue_uri: str):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self.logger = logger
        self.service_queue_uri = service_queue_uri or ''

    def connect(self) -> None:
        if self.connection:
            return

        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.service_queue_uri))
        except Exception as err:
            self.logger.error(f"Error connecting to RabbitMQ: {err}")
            raise

    def create_channel(self) -> None:
        if self.channel:
            return

        if not self.connection:
            self.connect()

        try:
            self.channel = self.connection.channel()
        except Exception as err:
            self.logger.error(f"Error creating RabbitMQ channel: {err}")
            raise

    def get_channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        if not self.channel:
            self.create_channel()

        if not self.channel:
            err = Exception('RabbitMQ channel is not available.')
            self.logger.error(err)
            raise err

        return self.channel