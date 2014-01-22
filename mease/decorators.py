# -*- coding: utf-8 -*-

__all__ = ('method_decorator',)


def method_decorator(method):
    def wrap(instance, function=None, *args, **kwargs):
        def inner_wrap(callback):
            method(instance, callback, *args, **kwargs)
        if function:
            return inner_wrap(function)
        return inner_wrap
    return wrap
