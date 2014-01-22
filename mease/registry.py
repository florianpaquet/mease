# -*- coding: utf-8 -*-
import re
import json
from concurrent.futures import ThreadPoolExecutor

from .decorators import method_decorator


class Mease(object):
    """
    Registry for mease callbacks
    """
    def __init__(self, backend_class, settings={}, max_workers=20, async=True):
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

        # Executor
        self.async = async

        if self.async:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)

    # -- Registers

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
    def sender(self, func, routing=None, routing_re=None):
        """
        Registers a sender function
        """
        if routing and not isinstance(routing, list):
            routing = [routing]

        if routing_re and not isinstance(routing_re, list):
            routing_re = [routing_re]
            routing_re[:] = [re.compile(r) for r in routing_re]

        self.senders.append((func, routing, routing_re))

    # -- Callers

    def submit(self, func, *args, **kwargs):
        """
        Submits callbacks to the executor or runs thems
        """
        if self.async:
            self.executor.submit(func, *args, **kwargs)
        else:
            func(*args, **kwargs)

    def call_openers(self, client, clients_list):
        """
        Calls openers callbacks
        """
        for func in self.openers:
            self.submit(func, client, clients_list)

    def call_closers(self, client, clients_list):
        """
        Calls closers callbacks
        """
        for func in self.closers:
            self.submit(func, client, clients_list)

    def call_receivers(self, client, clients_list, message):
        """
        Calls receivers callbacks
        """
        # Try to parse JSON
        try:
            json_message = json.loads(message)
        except ValueError:
            json_message = None

        for func, to_json in self.receivers:

            # Check if json version is available
            if to_json:
                if json_message is None:
                    continue
                msg = json_message
            else:
                msg = message

            # Call callback
            self.submit(func, client, clients_list, msg)

    def call_senders(self, routing, clients_list, *args, **kwargs):
        """
        Calls senders callbacks
        """
        for func, routings, routings_re in self.senders:
            call_callback = False

            # Message is published globally
            if routing is None or (routings is None and routings_re is None):
                call_callback = True

            # Message is not published globally
            else:

                # Message is catched by a string routing key
                if routings and routing in routings:
                    call_callback = True

                # Message is catched by a regex routing key
                if routings_re and any(r.match(routing) for r in routings_re):
                    call_callback = True

            if call_callback:
                self.submit(func, routing, clients_list, *args, **kwargs)

    # -- Publisher

    def publish(self, *args, **kwargs):
        """
        Publishes a message
        """
        # Connect to subscriber on first use
        if not self.publisher.__connected:
            self.publisher.__connected = True
            self.publisher.connect()

        self.submit(self.publisher.publish, *args, **kwargs)

    # -- Websocket

    def run_websocket_server(self, port=9090, autoreload=False):
        """
        Runs Tornado websocket server (blocking)
        """
        from .server import WebSocketServer

        ws_server = WebSocketServer(self, port, autoreload)
        ws_server.run()
