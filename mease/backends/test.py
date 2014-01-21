# -*- coding: utf-8 -*-
from .base import BasePublisher
from .base import BaseSubscriber
from .base import BaseBackend


class BasePublisher(BasePublisher):
    """
    Base publisher that handles outgoing messages
    """
    def connect(self):
        pass

    def publish(self, *args, **kwargs):
        pass


class BaseSubscriber(BaseSubscriber):
    """
    Base subscriber class that handles incoming messages
    """
    def connect(self):
        pass


class TestBackend(BaseBackend):
    """
    Base backend with a publisher and a subscriber class
    """
    publisher_class = BasePublisher
    subscriber_class = BaseSubscriber
