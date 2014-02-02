# -*- coding: utf-8 -*-
import re
import json

from .decorators import method_decorator
from .messages import ON_SEND

__all__ = ('Mease',)


class Mease(object):
    """
    Registry for mease callbacks
    """
    def __init__(self, backend_class, backend_settings={}):
        """
        Inits a registry
        """
        # Backend
        self.backend = backend_class(backend_settings)

        self.publisher = self.backend.get_publisher()
        self.publisher.connect()

        self.subscriber = self.backend.get_subscriber()

        # Callbacks
        self.openers = []
        self.closers = []
        self.receivers = []
        self.senders = []

    def _get_registry_names(self, registry):
        """
        Returns functions names for a registry
        """
        return ', '.join(
            f.__name__ if not isinstance(f, tuple) else f[0].__name__
            for f in getattr(self, registry, []))

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

        if routing_re:
            if not isinstance(routing_re, list):
                routing_re = [routing_re]
            routing_re[:] = [re.compile(r) for r in routing_re]

        self.senders.append((func, routing, routing_re))

    # -- Callers

    def call_openers(self, client, clients_list):
        """
        Calls openers callbacks
        """
        for func in self.openers:
            func(client, clients_list)

    def call_closers(self, client, clients_list):
        """
        Calls closers callbacks
        """
        for func in self.closers:
            func(client, clients_list)

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
            func(client, clients_list, msg)

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
                func(routing, clients_list, *args, **kwargs)

    # -- Publisher

    def publish(self, message_type=ON_SEND, client_id=None, client_storage=None,
                *args, **kwargs):
        """
        Publishes a message
        """
        self.publisher.publish(
            message_type, client_id, client_storage, *args, **kwargs)

    # -- Websocket

    def run_websocket_server(self, host='localhost', port=9090, debug=False):
        """
        Runs websocket server
        """
        from .server import MeaseWebSocketServerFactory

        websocket_factory = MeaseWebSocketServerFactory(
            mease=self, host=host, port=port, debug=debug)
        websocket_factory.run_server()
