# -*- coding: utf-8 -*-

import time
import typing as t

import ticker


class Ticker(ticker.Base):
    def __init__(self, interval: float, timeout: float):
        if interval > timeout:
            raise ValueError("interval cannot be greater tan timeout")

        self._interval = interval
        super().__init__(timeout)

    @property
    def interval(self) -> int:
        return self._interval

    def run(self) -> t.Iterator[int]:
        start = time.perf_counter_ns()

        while not self.done:
            now = time.perf_counter_ns()

            yield now

            if (now - start) * ticker.NANOSECOND > self._timeout:
                self._expired = True
                break

            time.sleep(self.interval)
