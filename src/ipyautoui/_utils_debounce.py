# https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html#Debouncing
# NOTE: currently not in use

import asyncio

# from threading import Timer
# ^ this can replace the Timer class below... not sure when / why this makes sense...


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback

    async def _job(self):
        await asyncio.sleep(self._timeout)
        self._callback()

    def start(self):
        self._task = asyncio.ensure_future(self._job())

    def cancel(self):
        self._task.cancel()


def debounce(wait):
    """Decorator that will postpone a function's
    execution until after `wait` seconds
    have elapsed since the last time it was invoked."""

    def decorator(fn):
        timer = None

        def debounced(*args, **kwargs):
            nonlocal timer

            def call_it():
                fn(*args, **kwargs)

            if timer is not None:
                timer.cancel()
            timer = Timer(wait, call_it)
            timer.start()

        return debounced

    return decorator
