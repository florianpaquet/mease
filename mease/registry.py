# -*- coding: utf-8 -*-
from .decorators import method_decorator


class Mease(object):
    """
    Registry for mease callbacks
    """
    def __init__(self, backend, settings):
        """
        Inits a registry
        """
        self.backend = backend
        self.settings = settings

        # Publisher
        self.publisher = backend.publisher_class(settings)
        self.publisher.connect()

        # Subscriber
        self.subscriber = backend.subscriber_class(settings)

        # Callbacks
        self.openers = []
        self.closers = []
        self.receivers = []
        self.senders = []

    def opener(self, func):
        """
        Registers an opener function
        """
        self.openers.append(func)

    def closer(self, func):
        """
        Registers a closer function
        """
        self.closers.append(func)

    @method_decorator
    def receiver(self, func=None, json=False):
        """
        Registers a receiver function
        """
        self.receivers.append((func, json))

    @method_decorator
    def sender(self, func, routing=None):
        """
        Registers a sender function
        """
        if not isinstance(routing, list):
            routing = [routing]
        self.senders.append((func, routing))

    def publish(self, *args, **kwargs):
        """
        Publishes a message
        """
        self.publisher.publish(*args, **kwargs)
