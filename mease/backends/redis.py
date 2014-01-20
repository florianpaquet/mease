# -*- coding: utf-8 -*-
import redis
import pickle
import logging
from toredis import Client

from .base import BasePublisher
from .base import BaseSubscriber

LOGGER = logging.getLogger('mease.websocket_server')


class RedisPublisher(BasePublisher):
    """
    Publisher using Redis PUB
    """
    def __init__(self, settings):
        # TODO : DRY
        self.host = self.get_setting(settings, 'BACKEND', 'HOST', 'localhost')
        self.port = self.get_setting(settings, 'BACKEND', 'PORT', 6379)
        self.channel = self.get_setting(settings, 'BACKEND', 'CHANNEL', 'mease')

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


class RedisSubscriber(BaseSubscriber):
    """
    Subscriber using Redis SUB
    """
    def __init__(self, settings):
        # TODO : DRY
        self.host = self.get_setting(settings, 'BACKEND', 'HOST', 'localhost')
        self.port = self.get_setting(settings, 'BACKEND', 'PORT', 6379)
        self.channel = self.get_setting(settings, 'BACKEND', 'CHANNEL', 'mease')

    def connect(self):
        """
        Connects to Redis
        """
        LOGGER.info("Connecting to Redis on {host}:{port}".format(
            host=self.host, port=self.port))

        # Connect
        self.client = Client()
        self.client.connect(host=self.host, port=self.port)

        LOGGER.info("Successfully connected to Redis")

        # Subscribe to channel
        self.client.subscribe(self.channel, callback=self.on_message)

        LOGGER.debug("Subscribed to [{channel}] Redis channel".format(
            channel=self.channel))

    def on_message(self, message):
        """
        Redis pubsub callback
        """
        event, channel, data = message

        if event.decode() == 'message':
            routing, args, kwargs = pickle.loads(data)
            self.dispatch_message(routing, args, kwargs)


class RedisBackend(object):
    """
    Redis Backend using PUB/SUB
    """
    publisher_class = RedisPublisher
    subscriber_class = RedisSubscriber
