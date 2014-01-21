# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger('mease.websocket_server')


class BasePublisher(object):
    """
    Base publisher that handles outgoing messages
    """
    def connect(self):
        raise NotImplementedError(
            "You need to implement your `connect` method for your publisher")

    def publish(self, *args, **kwargs):
        raise NotImplementedError(
            "You need to implement your `publish` method for your publisher")


class BaseSubscriber(object):
    """
    Base subscriber class that handles incoming messages
    """
    def connect(self):
        raise NotImplementedError(
            "You need to implement your `connect` method for your subscriber")

    def dispatch_message(self, routing, args, kwargs):
        """
        Calls callback functions
        """
        logger.debug("Backend message on [{routing}] route : {args} {kwargs}".format(
            routing=routing, args=args, kwargs=kwargs))

        self.application._mease.call_senders(
            routing, self.application.clients, *args, **kwargs)


class BaseBackend(object):
    """
    Base backend with a publisher and a subscriber class
    """
    publisher_class = BasePublisher
    subscriber_class = BaseSubscriber

    def __init__(self, settings):
        self.settings = settings

    def get_publisher_kwargs(self):
        """
        Additional kwargs for publisher instance
        """
        return {}

    def get_publisher(self):
        """
        Returns a publisher instance
        """
        return self.publisher_class(**self.get_publisher_kwargs())

    def get_subscriber_kwargs(self):
        """
        Additional kwargs for subscriber instance
        """
        return {}

    def get_subscriber(self):
        """
        Returns a subscriber instance
        """
        return self.subscriber_class(**self.get_subscriber_kwargs())
