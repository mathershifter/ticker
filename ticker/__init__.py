# -*- coding: utf-8 -*-

from ticker.base import Base, TickerStopped, TickerExpired
from ticker.ticker import Ticker
from ticker.timer import Timer

SECOND = 1  # 1000 * MILLISECOND
MILLISECOND = SECOND / 1000
MICROSECOND = MILLISECOND / 1000
NANOSECOND = MICROSECOND / 1000
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE

__all__ = ["Base", "Ticker", "Timer", "TickerStopped", "TickerExpired"]