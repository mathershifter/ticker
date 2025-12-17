# -*- coding: utf-8 -*-

import queue
import threading
import typing as t

from abc import ABC, abstractmethod


class TickerExpired(Exception): ...


class TickerStopped(Exception): ...


class Base(ABC):
    def __init__(self, timeout: float | None, strict=False):
        self._timeout = timeout
        self._strict = strict

        # Queue used to publish the firing timestamp. Consumers call
        # :meth:``wait`` / :meth:``get`` which block on this queue.
        self._queue = queue.Queue()
        self._sentinel = threading.Event()

        self._expired: bool = False

        # Run the timer loop in a background daemon thread.
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()

    @property
    def done(self):
        return self._sentinel.is_set() or self._queue.is_shutdown or self._expired

    stopped = done

    @property
    def expired(self) -> bool:
        return self._expired

    @expired.setter
    def expired(self, v: bool) -> None:
        self._expired = v

    @property
    def queue(self) -> queue.Queue:
        return self._queue

    @property
    def sentinel(self) -> threading.Event:
        return self._sentinel

    @property
    def timeout(self) -> int | float:
        return self._timeout

    def start(self):
        self._thread.start()

    def stop(self):
        self._sentinel.set()

        if not self._queue.is_shutdown:
            self._queue.shutdown()

    def _run(self) -> None:
        for ts in self.run():
            self._queue.put(ts)

        self.stop()

    def wait(self) -> int:
        try:
            return self._queue.get()
        except queue.ShutDown:
            if self.expired:
                raise TickerExpired(
                    "timer expired, but queue was shutdown "
                    "and drained before get was called..."
                )
            raise TickerStopped("timer was stopped before deadline")

    @abstractmethod
    def run(self) -> t.Iterator[int]: ...
