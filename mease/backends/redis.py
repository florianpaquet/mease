# -*- coding: utf-8 -*-
from __future__ import absolute_import
from threading import Thread

from .. import logger

try:
    import redis
except ImportError:
    logger.critical("Missing backend dependency (redis)")
    raise

from .base import BasePublisher
from .base import BaseSubscriber
from .base import BaseBackend

__all__ = ('RedisPublisher', 'RedisSubscriber', 'RedisBackend')


class RedisBackendMixin(object):
    """
    Redis backend mixin that sets connection settings
    """
    def __init__(self, host, port, password, channel, *args, **kwargs):
        super(RedisBackendMixin, self).__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.password = password
        self.channel = channel

    def connect(self):
        """
        Connects to publisher
        """
        self.client = redis.Redis(
            host=self.host, port=self.port, password=self.password)


class RedisPublisher(RedisBackendMixin, BasePublisher):
    """
    Publisher using Redis PUB
    """
    def publish(self, message_type, client_id, client_storage, *args, **kwargs):
        """
        Publishes a message
        """
        p = self.pack(message_type, client_id, client_storage, args, kwargs)
        self.client.publish(self.channel, p)

    def exit(self):
        """
        Closes the connection
        """
        self.client.connection_pool.disconnect()


class RedisSubscriber(RedisBackendMixin, BaseSubscriber):
    """
    Subscriber using Redis SUB
    """
    def connect(self):
        """
        Connects to Redis
        """
        logger.info("Connecting to Redis on {host}:{port}...".format(
            host=self.host, port=self.port))

        super(RedisSubscriber, self).connect()
        logger.info("Successfully connected to Redis")

        # Subscribe to channel
        self.pubsub = self.client.pubsub()
        self.pubsub.subscribe(self.channel)

        logger.info("Subscribed to [{channel}] Redis channel".format(
            channel=self.channel))

        # Start listening
        t = Thread(target=self.listen)
        t.setDaemon(True)
        t.start()

    def listen(self):
        """
        Listen for messages
        """
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                message_type, client_id, client_storage, args, kwargs = self.unpack(
                    message['data'])

                self.dispatch_message(
                    message_type, client_id, client_storage, args, kwargs)

    def exit(self):
        """
        Closes the connection
        """
        self.pubsub.unsubscribe()
        self.client.connection_pool.disconnect()

        logger.info("Connection to Redis closed")


class RedisBackend(BaseBackend):
    """
    Redis Backend using PUB/SUB
    """
    name = "Redis"
    publisher_class = RedisPublisher
    subscriber_class = RedisSubscriber

    def __init__(self, *args, **kwargs):
        super(RedisBackend, self).__init__(*args, **kwargs)

        self.host = self.settings.get('HOST', 'localhost')
        self.port = self.settings.get('PORT', 6379)
        self.channel = self.settings.get('CHANNEL', 'mease')
        self.password = self.settings.get('PASSWORD', None)

    def get_kwargs(self):
        """
        Returns kwargs for both publisher and subscriber classes
        """
        return {
            'host': self.host,
            'port': self.port,
            'channel': self.channel,
            'password': self.password
        }

    get_publisher_kwargs = get_kwargs
    get_subscriber_kwargs = get_kwargs
