# -*- coding: utf-8 -*-
from ..mixins import SettingsMixin


class BaseSubscriber(SettingsMixin):
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
        for func, routings in self.application.mease.senders:
            if routing is None or routings is None or routing in routings:
                self.application.executor.submit(
                    func, routing, self.application.clients, *args, **kwargs)


class BasePublisher(SettingsMixin):
    """
    Base publisher that handles outgoing messages
    """
    def publish(self, *args, **kwargs):
        raise NotImplementedError(
            "You need to implement your `publish` method for your publisher")
