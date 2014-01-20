# -*- coding: utf-8 -*-
import json
import logging
import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.websocket
from concurrent.futures import ThreadPoolExecutor

from .mixins import SettingsMixin

__all__ = ('WebSocketServer',)
LOGGER = logging.getLogger('mease.websocket_server')


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        """
        Called when a client opens a websocket connection
        """
        # Init storage
        self.storage = {}

        # Call openers callbacks
        for func in self.application.mease.openers:
            self.application.executor.submit(func, self, self.application.clients)

        # Append client to clients list
        if self not in self.application.clients:
            self.application.clients.append(self)

    def on_close(self):
        """
        Called when a client closes a websocket connection
        """
        # Call closer callbacks
        for func in self.application.mease.closers:
            self.application.executor.submit(func, self, self.application.clients)

        # Remove client from clients list
        if self in self.application.clients:
            self.application.clients.remove(self)

    def on_message(self, message):
        """
        Called when a client sends a message through websocket
        """
        # Parse JSON
        try:
            json_message = json.loads(message)
        except ValueError:
            json_message = None

        # Call receiver callbacks
        for func, to_json in self.application.mease.receivers:

            if to_json:
                if json_message is None:
                    continue
                msg = json_message
            else:
                msg = message

            self.application.executor.submit(
                func, self, msg, self.application.clients)

    def send(self, *args, **kwargs):
        self.write_message(*args, **kwargs)


class WebSocketServer(SettingsMixin):

    def __init__(self, mease):
        """
        Inits websocket server
        """
        self.mease = mease

        # Tornado loop
        self.ioloop = tornado.ioloop.IOLoop.instance()

        # Tornado application
        self.debug = self.get_setting(mease.settings, 'SERVER', 'DEBUG', True)
        self.port = self.get_setting(mease.settings, 'SERVER', 'PORT', 9090)

        self.application = tornado.web.Application([
            (r'/', WebSocketHandler),
        ], debug=self.debug)

        # Init application storage
        self.application.storage = {}

        # Clients list
        self.application.clients = []

        # Registry
        self.application.mease = mease

        # Executor
        self.application.executor = ThreadPoolExecutor(max_workers=20)  # SETTING REQUIRED

        # Connect to subscriber
        self.mease.subscriber.connect()
        self.mease.subscriber.application = self.application

    def run(self):
        """
        Starts websocket server
        """
        self.application.listen(self.port)
        self.ioloop.start()
