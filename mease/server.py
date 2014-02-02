# -*- coding: utf-8 -*-
import json
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory
from uuid import uuid1
from twisted.internet import reactor

from . import logger
from .messages import ON_OPEN
from .messages import ON_CLOSE
from .messages import ON_RECEIVE

__all__ = ('MeaseWebSocketServerProtocol', 'MeaseWebSocketServerFactory')


class MeaseWebSocketServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        """
        Called when a client opens a websocket connection
        """
        logger.debug("Connection opened ({peer})".format(peer=self.peer))

        self.storage = {}
        self._client_id = str(uuid1())

    def onOpen(self):
        """
        Called when a client has opened a websocket connection
        """
        self.factory.add_client(self)

        # Publish ON_OPEN message
        self.factory.mease.publisher.publish(
            message_type=ON_OPEN, client_id=self._client_id, client_storage=self.storage)

    def onClose(self, was_clean, code, reason):
        """
        Called when a client closes a websocket connection
        """
        logger.debug("Connection closed ({peer})".format(peer=self.peer))

        # Publish ON_CLOSE message
        self.factory.mease.publisher.publish(
            message_type=ON_CLOSE, client_id=self._client_id, client_storage=self.storage)

        self.factory.remove_client(self)

    def onMessage(self, payload, is_binary):
        """
        Called when a client sends a message
        """
        if not is_binary:
            payload = payload.decode('utf-8')

            logger.debug("Incoming message ({peer}) : {message}".format(
                peer=self.peer, message=payload))

            # Publish ON_RECEIVE message
            self.factory.mease.publisher.publish(
                message_type=ON_RECEIVE,
                client_id=self._client_id,
                client_storage=self.storage,
                message=payload)

    def sendMessage(self, payload, *args, **kwargs):
        """
        Logs message
        """
        logger.debug("Outgoing message for ({peer}) : {message}".format(
            peer=self.peer, message=payload))

        WebSocketServerProtocol.sendMessage(self, payload, *args, **kwargs)

    def send(self, payload, *args, **kwargs):
        """
        Alias for WebSocketServerProtocol `sendMessage` method
        """
        if isinstance(payload, (list, dict)):
            payload = json.dumps(payload)

        self.sendMessage(payload.encode(), *args, **kwargs)


class MeaseWebSocketServerFactory(WebSocketServerFactory):
    def __init__(self, mease, host, port, debug):
        self.host = host
        self.port = port

        self.address = 'ws://{host}:{port}'.format(host=host, port=self.port)
        WebSocketServerFactory.__init__(self, self.address, debug=debug)

        self.storage = {}
        self.clients_list = set()

        self.mease = mease

        # Connect to subscriber
        logger.debug("Connecting to backend ({backend_name})...".format(
            backend_name=self.mease.backend.name))

        self.mease.subscriber.connect()
        self.mease.subscriber.factory = self

        # Log registered callbacks
        logger.debug("Registered callback functions :")

        logger.debug(
            "Openers : [%s]" % self.mease._get_registry_names('openers'))
        logger.debug(
            "Closers : [%s]" % self.mease._get_registry_names('closers'))
        logger.debug(
            "Receivers : [%s]" % self.mease._get_registry_names('receivers'))
        logger.debug(
            "Senders : [%s]" % self.mease._get_registry_names('senders'))

    def add_client(self, client):
        """
        Adds a client to the clients list
        """
        self.clients_list.add(client)

    def remove_client(self, client):
        """
        Removes a client from the client list
        """
        self.clients_list.discard(client)

    def run_server(self):
        """
        Runs the WebSocket server
        """
        self.protocol = MeaseWebSocketServerProtocol

        reactor.listenTCP(port=self.port, factory=self, interface=self.host)

        logger.info("Websocket server listening on {address}".format(
            address=self.address))

        reactor.run()
