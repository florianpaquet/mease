# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.websocket

from . import logger

__all__ = ('WebSocketServer',)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
    Tornado websocket handler
    """
    def open(self):
        """
        Called when a client opens a websocket connection
        """
        logger.debug("Connection opened ({ip})".format(ip=self.request.remote_ip))

        # Initialize an empty client storage
        self.storage = {}

        # Call openers callbacks
        self.application._mease.call_openers(self, self.application.clients)

        # Append client to clients list
        self.application.clients.add(self)

    def on_close(self):
        """
        Called when a client closes a websocket connection
        """
        logger.debug("Connection closed ({ip})".format(ip=self.request.remote_ip))

        # Call closer callbacks
        self.application._mease.call_closers(self, self.application.clients)

        # Remove client from clients list
        self.application.clients.discard(self)

    def on_message(self, message):
        """
        Called when a client sends a message through websocket
        """
        logger.debug("Incoming message ({ip}) : {message}".format(
            ip=self.request.remote_ip, message=message))

        # Call receiver callbacks
        self.application._mease.call_receivers(self, self.application.clients, message)

    def write_message(self, message, *args, **kwargs):
        """
        Logs message
        """
        logger.debug("Outgoing message for ({ip}) : {message}".format(
            ip=self.request.remote_ip, message=message))

        super(WebSocketHandler, self).write_message(message, *args, **kwargs)

    def send(self, *args, **kwargs):
        """
        Alias for WebSocketHandler `write_message` method
        """
        self.write_message(*args, **kwargs)


class WebSocketServer(object):
    """
    Tornado websocket server
    """
    def __init__(self, mease, port, address, url, autoreload):
        """
        Inits websocket server
        """
        self.mease = mease
        self.port = port
        self.address = address
        self.url = url

        # Tornado app
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.application = tornado.web.Application([
            (url, WebSocketHandler),
        ], debug=autoreload)

        # Initialize an empty application storage
        self.application.storage = {}

        # Initialize an empty clients list
        self.application.clients = set()

        # Expose mease instance to Tornado application
        self.application._mease = self.mease

        # Connect to subscriber
        logger.debug("Connecting to backend ({backend_name})...".format(
            backend_name=self.mease.backend.name))

        self.mease.subscriber.connect()
        self.mease.subscriber.application = self.application

        # Log registered callbacks
        logger.debug("Registered callback functions :")

        logger.debug(
            "Openers : [%s]" % self._get_registry_names(self.mease.openers))
        logger.debug(
            "Closers : [%s]" % self._get_registry_names(self.mease.closers))
        logger.debug(
            "Receivers : [%s]" % self._get_registry_names(self.mease.receivers))
        logger.debug(
            "Senders : [%s]" % self._get_registry_names(self.mease.senders))

    def _get_registry_names(self, registry):
        """
        Returns functions names for a registry
        """
        return ', '.join(
            f.__name__ if not isinstance(f, tuple) else f[0].__name__
            for f in registry)

    def run(self):
        """
        Starts websocket server (blocking)
        """
        self.application.listen(port=self.port, address=self.address)

        logger.info("Websocket server listening on {address}:{port} (URL: {url})".format(
            address=self.address, port=self.port, url=self.url))

        self.ioloop.start()
