# -*- coding: utf-8 -*-


class FakeClient(object):
    def __init__(self, storage, factory):
        self.storage = storage
        self.factory = factory

    def send(self, *args, **kwargs):
        pass
