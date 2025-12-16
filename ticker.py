# -*- coding: utf-8 -*-

import queue
import time
import threading


class TickerExpired(Exception): ...


class TickerStopped(Exception): ...


class TimerExpired(Exception): ...


class TimerStopped(Exception): ...


SECOND = 1  # 1000 * MILLISECOND
MILLISECOND = SECOND / 1000
MICROSECOND = MILLISECOND / 1000
NANOSECOND = MICROSECOND / 1000
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE


class Timer:
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

    @property
    def timeout(self) -> int | float:
        return self._timeout

    def _run(self):
        if self.timeout is not None:
            time.sleep(self.timeout)

        self._queue.put(time.perf_counter_ns())

        self.stop()

    def start(self):
        self._thread.start()

        # self._start_time = time.perf_counter_ns()

    def stop(self):
        self._sentinel.set()

        if not self._queue.is_shutdown:
            self._queue.shutdown()

        # self._stop_time = time.perf_counter_ns()

    def wait(self) -> int:
        try:
            return self._queue.get()

        except queue.ShutDown:
            if self.expired:
                raise TimerExpired(
                    "timer expired, but queue was shutdown "
                    "and drained before get was called..."
                )
            raise TimerStopped("timer was stopped before deadline")


class Ticker(Timer):
    def __init__(self, interval: float, timeout: float):
        if interval > timeout:
            raise ValueError("interval cannot be greater tan timeout")

        self._interval = interval
        super().__init__(timeout)

    @property
    def interval(self) -> int:
        return self._interval

    def wait(self) -> int:
        try:
            return self._queue.get()
        except queue.ShutDown:
            if self.expired:
                raise TickerExpired
            raise TickerStopped

    def _run(self):
        start = time.perf_counter_ns()

        while not self.done:
            now = time.perf_counter_ns()

            self._queue.put(now)

            if (now - start) * NANOSECOND > self._timeout:
                self._expired = True
                break

            time.sleep(self.interval)

        self.stop()
