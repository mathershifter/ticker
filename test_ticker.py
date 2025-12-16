# -*- coding: utf-8 -*-

import pytest
import time

import ticker

def test_ticker_with():
    with ticker.Ticker(1, 5) as tkr:
        # print(f"INTERVAL: {tkr.interval} {tkr.timeout}")
        while not tkr.done:
            tkr.wait()
            

def test_expire():
    tkr = ticker.Ticker(1, 2)
    tkr.start()
    with pytest.raises(ticker.TickerExpired):
        while True:
            tkr.wait()
            
    assert tkr.done


def test_cancel():
    tkr = ticker.Ticker(1, 30)
    
    tkr.start()
    tkr.stop()

    with pytest.raises(ticker.TickerStopped):
        while True:
            tkr.wait()


def test_timer_expire():
    with ticker.Timer(1, True):
        time.sleep(5)

@pytest.mark.parametrize("timeout", [
    # (.03, ticker.MINUTE, 1e-4),
    2.0 * ticker.SECOND,
    100.0 * ticker.MILLISECOND,
    # (10, ticker.MILLISECOND),
    # (1, ticker.MILLISECOND),
    # (100, ticker.MICROSECOND)
])
def test_timer(timeout):
    timeout = timeout
    
    start = time.perf_counter_ns()
    with ticker.Timer(timeout) as tmr:
        end = tmr.wait()
    
    assert (end - start) / 1_000_000_000 == pytest.approx(timeout, rel=1e-1), \
        f"timer did not end on time [{tmr.duration} ~= {timeout}"

def test_many():
    # with pytest.raises(ticker.ManagerMaxThreadsExceeded):
    for i in range(0, 1024):
        tmr = ticker.Timer(1)
        tmr.start()
    
    time.sleep(5)