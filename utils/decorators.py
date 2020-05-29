from functools import wraps
from threading import Thread

from utils.shortcuts import iredirect


def doublewrap(f):
    """
    a decorator decorator, allowing the decorator to be used as:
    @decorator(with, arguments, and=kwargs)
    or
    @decorator
    """
    @wraps(f)
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return f(args[0])
        else:
            # decorator arguments
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec


def make_async(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        t.start()
    return wrapper


def prepod_only(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        request = __find_request(*args)

        if not request.user.is_superuser and request.user.prepod.count() == 0:
            return iredirect('main:index')
        return view(*args, **kwargs)
    return wrapper


# is not decorator
def __find_request(*args):
    for arg in args:
        if type(arg).__name__ == 'WSGIRequest':
            return arg
    return None