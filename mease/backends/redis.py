# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pickle
import logging

try:
    import redis
except ImportError:
    raise ImportError('Missing backend dependency (redis)')
try:
    from toredis import Client
except ImportError:
    raise ImportError('Missing backend dependency (toredis-mease)')

from .base import BasePublisher
from .base import BaseSubscriber
from .base import BaseBackend

logger = logging.getLogger('mease.websocket_server')


class RedisBackendMixin(object):
    """
    Redis backend mixin that sets connection settings
    """
    def __init__(self, host, port, channel, *args, **kwargs):
        super(RedisBackendMixin, self).__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.channel = channel


class RedisPublisher(RedisBackendMixin, BasePublisher):
    """
    Publisher using Redis PUB
    """
    def connect(self):
        """
        Connects to publisher
        """
        self.client = redis.Redis(host=self.host, port=self.port)

    def publish(self, routing=None, *args, **kwargs):
        """
        Publishes a message
        """
        p = pickle.dumps((routing, args, kwargs), protocol=2)
        self.client.publish(self.channel, p)


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

        # Connect
        self.client = Client()
        self.client.connect(host=self.host, port=self.port)

        logger.info("Successfully connected to Redis")

        # Subscribe to channel
        self.client.subscribe(self.channel, callback=self.on_message)

        logger.info("Subscribed to [{channel}] Redis channel".format(
            channel=self.channel))

    def on_message(self, message):
        """
        Redis pubsub callback
        """
        event, channel, data = message

        if event.decode() == 'message':
            routing, args, kwargs = pickle.loads(data)
            self.dispatch_message(routing, args, kwargs)


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

    def get_kwargs(self):
        """
        Returns kwargs for both publisher and subscriber classes
        """
        return {
            'host': self.host,
            'port': self.port,
            'channel': self.channel
        }

    get_publisher_kwargs = get_kwargs
    get_subscriber_kwargs = get_kwargs
