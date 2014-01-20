# -*- coding: utf-8 -*-

__all__ = ('base', 'opener', 'closer', 'receiver', 'sender')


def method_decorator(method):
    def wrap(instance, *args, **kwargs):
        def inner_wrap(func):
            method(instance, func, *args, **kwargs)
        return inner_wrap
    return wrap
