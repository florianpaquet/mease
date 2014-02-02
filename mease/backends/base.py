# -*- coding: utf-8 -*-
import pickle
from twisted.internet import reactor

from .. import logger
from ..fake import FakeClient
from ..messages import ON_OPEN
from ..messages import ON_CLOSE
from ..messages import ON_RECEIVE
from ..messages import ON_SEND
from ..messages import MESSAGES_TYPES

__all__ = ('BasePublisher', 'BaseSubscriber', 'BaseBackend')


class BasePublisher(object):
    """
    Base publisher that handles outgoing messages
    """
    def __init__(self, *args, **kwargs):
        reactor.addSystemEventTrigger('before', 'shutdown', self.exit)

    def connect(self):
        """
        Connects to the publisher
        """
        raise NotImplementedError(
            "You need to implement the `connect` method for your publisher")

    def publish(self, *args, **kwargs):
        """
        Publishes a message
        """
        raise NotImplementedError(
            "You need to implement the `publish` method for your publisher")

    def pack(self, message_type, client_id, client_storage, args, kwargs):
        """
        Packs a message
        """
        return pickle.dumps(
            (message_type, client_id, client_storage, args, kwargs), protocol=2)

    def exit(self):
        """
        Called before closing the connection to publisher
        """
        pass


class BaseSubscriber(object):
    """
    Base subscriber class that handles incoming messages
    """
    def __init__(self, *args, **kwargs):
        reactor.addSystemEventTrigger('before', 'shutdown', self.exit)

    def connect(self):
        """
        Connects to the subscriber
        """
        raise NotImplementedError(
            "You need to implement the `connect` method for your subscriber")

    def unpack(self, message):
        """
        Unpacks a message
        """
        return pickle.loads(message)

    def dispatch_message(self, message_type, client_id, client_storage, args, kwargs):
        """
        Calls callback functions
        """
        logger.debug("Backend message ({message_type}) : {args} {kwargs}".format(
            message_type=dict(MESSAGES_TYPES)[message_type], args=args, kwargs=kwargs))

        if message_type in [ON_OPEN, ON_CLOSE, ON_RECEIVE]:
            # Find if client exists in clients_list
            client = next(
                (c for c in self.factory.clients_list if c._client_id == client_id), None)

            # Create a fake client if it doesn't exists
            if not client:
                client = FakeClient(storage=client_storage, factory=self.factory)

        if message_type == ON_OPEN:
            reactor.callInThread(
                self.factory.mease.call_openers, client, self.factory.clients_list)

        elif message_type == ON_CLOSE:
            reactor.callInThread(
                self.factory.mease.call_closers, client, self.factory.clients_list)

        elif message_type == ON_RECEIVE:
            reactor.callInThread(
                self.factory.mease.call_receivers,
                client,
                self.factory.clients_list,
                kwargs.get('message', ''))

        elif message_type == ON_SEND:
            routing = kwargs.pop('routing')

            reactor.callInThread(
                self.factory.mease.call_senders,
                routing,
                self.factory.clients_list,
                *args,
                **kwargs)

    def exit(self):
        """
        Called before closing the connection to subscriber
        """
        pass


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
