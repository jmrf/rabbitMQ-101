import asyncio
import time
from functools import wraps
from typing import Callable


def fire_and_forget(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, *kwargs)

    return wrapped


def timeit(func: Callable) -> Callable:
    @wraps(func)
    def timed_wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        delta = time.time() - start
        return res, delta

    return timed_wrapper
