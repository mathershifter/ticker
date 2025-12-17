# -*- coding: utf-8 -*-

import time

from ticker.base import Base

class Timer(Base):
    def run(self):
        if self.timeout is not None:
            time.sleep(self.timeout)
        self.expired
        yield time.perf_counter_ns()

