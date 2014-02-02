# -*- coding: utf-8 -*-
from .base import BasePublisher
from .base import BaseSubscriber
from .base import BaseBackend

__all__ = ('TestPublisher', 'TestSubscriber', 'TestBackend')


class TestPublisher(BasePublisher):
    def connect(self):
        pass

    def publish(self, *args, **kwargs):
        pass


class TestSubscriber(BaseSubscriber):
    def connect(self):
        pass


class TestBackend(BaseBackend):
    """
    Base backend with a publisher and a subscriber class
    """
    name = "Test Backend"
    publisher_class = TestPublisher
    subscriber_class = TestSubscriber
