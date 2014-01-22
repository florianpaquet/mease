# -*- coding: utf-8 -*-
from functools import wraps

__all__ = ('passes_test',)


def passes_test(perm_func):
    def decored(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not perm_func(*args, **kwargs):
                return
            func(*args, **kwargs)
        return wrapper
    return decored
