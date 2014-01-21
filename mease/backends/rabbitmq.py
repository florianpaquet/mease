# -*- coding: utf-8 -*-
import pickle
import logging

try:
    import pika
    from pika.adapters.tornado_connection import TornadoConnection
except ImportError:
    raise ImportError('Missing backend dependency (pika)')

from .base import BasePublisher
from .base import BaseSubscriber
from .base import BaseBackend


logger = logging.getLogger('mease.websocket_server')


class RabbitMQBackendMixin(object):
    """
    RabbitMQ backend mixin that stores connection settings
    """
    def __init__(self, broker_url, queue, *args, **kwargs):
        super(RabbitMQBackendMixin, self).__init__(*args, **kwargs)

        self.broker_url = broker_url
        self.queue = queue

        self.params = pika.URLParameters(self.broker_url)


class RabbitMQPublisher(RabbitMQBackendMixin, BasePublisher):
    """
    RabbitMQ publisher
    """
    def connect(self):
        self.client = pika.BlockingConnection(self.params)
        self.channel = self.client.channel()

    def publish(self, routing=None, *args, **kwargs):
        """
        Publishes a message
        """
        p = pickle.dumps((routing, args, kwargs), protocol=2)
        self.channel.basic_publish(exchange='', routing_key=self.queue, body=p)


class RabbitMQSubscriber(RabbitMQBackendMixin, BaseSubscriber):
    """
    RabbitMQ subscriber
    """
    def __init__(self, *args, **kwargs):
        super(RabbitMQSubscriber, self).__init__(*args, **kwargs)

        self.connection = None
        self.consumer_tag = None
        self.channel = None

    def __connect(self):
        """
        Connects to RabbitMQ
        """
        logger.info("Connecting to RabbitMQ on {broker_url}...".format(
            broker_url=self.broker_url))

        return TornadoConnection(
            self.params, on_open_callback=self.on_connected, stop_ioloop_on_close=False)

    def connect(self):
        self.connection = self.__connect()

    def on_connected(self, connection):
        """
        Opens a channel after connection
        """
        logger.info("Successfully connected to RabbitMQ")

        self.connection.add_on_close_callback(self.on_closed)
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        """
        Declares a queue after channel connection
        """
        self.channel = channel
        self.channel.queue_declare(
            queue=self.queue,
            durable=True,
            exclusive=False,
            auto_delete=False,
            callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        """
        Registers a consumer on queue
        """
        logger.info("Subscribed to [{queue}] RabbitMQ queue".format(
            queue=self.queue))

        self.consumer_tag = self.channel.basic_consume(
            self.handle_delivery, queue=self.queue)

    def on_closed(self, connection, reply_code, reply_text):
        """
        On close
        """
        self.channel = None
        self.connection.add_timeout(2, self.reconnect)

    def reconnect(self):
        """
        Reconnects to amqp
        """
        logger.info(
            "Lost connection to RabbitMQ... Reconnecting to {broker_url}...".format(
                broker_url=self.broker_url))

        self.connection = self.connect()

    def handle_delivery(self, channel, method, header, body):
        """
        Handles message delivery
        """
        routing, args, kwargs = pickle.loads(body)

        # Dispatch to callbacks
        self.dispatch_message(routing, args, kwargs)

        self.acknowledge_message(method.delivery_tag)

    def acknowledge_message(self, delivery_tag):
        """
        Acknowledge message
        """
        self.channel.basic_ack(delivery_tag)


class RabbitMQBackend(BaseBackend):
    name = "RabbitMQ"
    publisher_class = RabbitMQPublisher
    subscriber_class = RabbitMQSubscriber

    def __init__(self, *args, **kwargs):
        super(RabbitMQBackend, self).__init__(*args, **kwargs)

        self.broker_url = self.settings.get(
            'BROKER_URL', 'amqp://guest:guest@localhost:5672//')
        self.queue = self.settings.get('QUEUE', 'mease')

    def get_kwargs(self):
        """
        Returns kwargs for both publisher and subscriber classes
        """
        return {
            'broker_url': self.broker_url,
            'queue': self.queue
        }

    get_publisher_kwargs = get_kwargs
    get_subscriber_kwargs = get_kwargs
