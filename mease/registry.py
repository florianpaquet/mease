# -*- coding: utf-8 -*-
from .decorators import method_decorator
from .server import WebSocketServer


class Mease(object):
    """
    Registry for mease callbacks
    """
    def __init__(self, backend_class, settings):
        """
        Inits a registry
        """
        # Backend
        self.backend = backend_class(settings)

        self.publisher = self.backend.get_publisher()
        self.publisher.__connected = False
        self.subscriber = self.backend.get_subscriber()

        # Callbacks
        self.openers = []
        self.closers = []
        self.receivers = []
        self.senders = []

    @method_decorator
    def opener(self, func):
        """
        Registers an opener function
        """
        self.openers.append(func)

    @method_decorator
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
        # Connect to subscriber on first use
        if not self.publisher.__connected:
            self.publisher.__connected = True
            self.publisher.connect()

        self.publisher.publish(*args, **kwargs)

    def run_websocket_server(self, port=9090, autoreload=False):
        """
        Runs Tornado websocket server (blocking)
        """
        ws_server = WebSocketServer(self, port, autoreload)
        ws_server.run()
