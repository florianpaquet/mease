# -*- coding: utf-8 -*-
from .. import logger
from threading import Thread

try:
    from kombu import Connection
    from kombu import Consumer
    from kombu import Exchange
    from kombu import Queue
    from kombu.common import eventloop
except ImportError:
    logger.critical("Missing backend dependency (kombu)")
    raise

from .base import BasePublisher
from .base import BaseSubscriber
from .base import BaseBackend

__all__ = ('RabbitMQPublisher', 'RabbitMQSubscriber', 'RabbitMQBackend')


class RabbitMQBackendMixin(object):
    """
    RabbitMQ backend mixin that stores connection settings
    """
    def __init__(self, broker_url, exchange_name, *args, **kwargs):
        super(RabbitMQBackendMixin, self).__init__(*args, **kwargs)

        self.broker_url = broker_url
        self.exchange_name = exchange_name

    def connect(self):
        """
        Connects to RabbitMQ
        """
        self.connection = Connection(self.broker_url)

        e = Exchange('mease', type='fanout', durable=False, delivery_mode=1)
        self.exchange = e(self.connection.default_channel)
        self.exchange.declare()

    def exit(self):
        """
        Closes the connection
        """
        self.connection.close()


class RabbitMQPublisher(RabbitMQBackendMixin, BasePublisher):
    """
    RabbitMQ publisher
    """
    def publish(self, message_type, client_id, client_storage, *args, **kwargs):
        """
        Publishes a message
        Uses `self.pack` instead of 'msgpack' serializer on kombu for backend consistency
        """
        if self.connection.connected:
            message = self.exchange.Message(
                self.pack(message_type, client_id, client_storage, args, kwargs))
            self.exchange.publish(message, routing_key='')


class RabbitMQSubscriber(RabbitMQBackendMixin, BaseSubscriber):
    """
    RabbitMQ subscriber
    """
    def connect(self):
        """
        Connects to RabbitMQ and starts listening
        """
        logger.info("Connecting to RabbitMQ on {broker_url}...".format(
            broker_url=self.broker_url))

        super(RabbitMQSubscriber, self).connect()

        q = Queue(exchange=self.exchange, exclusive=True, durable=False)

        self.queue = q(self.connection.default_channel)
        self.queue.declare()

        self.thread = Thread(target=self.listen)
        self.thread.setDaemon(True)
        self.thread.start()

    def listen(self):
        """
        Listens to messages
        """
        with Consumer(self.connection, queues=self.queue, on_message=self.on_message,
                      auto_declare=False):
            for _ in eventloop(self.connection, timeout=1, ignore_timeouts=True):
                    pass

    def on_message(self, message):
        """
        Handles message
        """
        message_type, client_id, client_storage, args, kwargs = self.unpack(
            message.body)

        self.dispatch_message(
            message_type, client_id, client_storage, args, kwargs)

        message.ack()

    def exit(self):
        """
        Closes the connection
        """
        super(RabbitMQSubscriber, self).exit()

        logger.info("Connection to RabbitMQ closed")


class RabbitMQBackend(BaseBackend):
    name = "RabbitMQ"
    publisher_class = RabbitMQPublisher
    subscriber_class = RabbitMQSubscriber

    def __init__(self, *args, **kwargs):
        super(RabbitMQBackend, self).__init__(*args, **kwargs)

        self.broker_url = self.settings.get(
            'BROKER_URL', 'amqp://guest:guest@localhost:5672//')
        self.exchange_name = self.settings.get('EXCHANGE', 'mease')

    def get_kwargs(self):
        """
        Returns kwargs for both publisher and subscriber classes
        """
        return {
            'broker_url': self.broker_url,
            'exchange_name': self.exchange_name
        }

    get_publisher_kwargs = get_kwargs
    get_subscriber_kwargs = get_kwargs
