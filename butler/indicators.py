import numpy as np


def sma(array, n=5):
    """
    Calculate the simple moving averages (SMA)

    :param array: the price array represented in python list
    :param n: the average period
    :return: the corresponding SMA which has the same length of the input array
    """
    ma = np.zeros(shape=(len(array), ))
    for i, val in enumerate(array):
        batch = array[max(i - n + 1, 0): i + 1]
        # ma.append(np.mean(batch))
        ma[i] = np.mean(batch)
    return ma


def ema(array, n=5):
    """
    Calculate the exponentially weighted averages (a.k.a. EMA) for a given array:
    v_t = beta * v_{t-1} + (1 - beta) * a_t

    (deprecated)
    The problem with the above equation is that the EMA will start off with very
    small numbers in the beginning, adding bias correction will solve this problem:
    v_t = v_t / (1 - beta ^ t)

    :param array: the price array given in form of a python list of floating numbers
    :param n: the period considered
    :return: the EMA
    """
    beta = 1 - 2 / (n + 1)
    ma = np.zeros(shape=(len(array),))
    for i, val in enumerate(array):
        if i == 0:
            ma[i] = val
            continue
        previous = ma[i - 1]
        current = beta * previous + (1 - beta) * val
        ma[i] = current
    return ma


def macd(array, a=12, b=26, c=9):
    """
    Calculates the MACD, MACD signal, and their differences (histogram)

    :param array: the price array represented as python list
    :param a: fast period length
    :param b: slow period length
    :param c: the average period length of the MACD itself
    :return: MACD, signal, and their difference
    """
    fast = ema(array, a)
    slow = ema(array, b)
    proper = fast - slow
    signal = ema(proper, c)
    diff = proper - signal
    return proper, signal, diff


def moving_std(array, n=5):
    """
    Calculate the moving standard deviation with a given sliding window

    :param array: the price array in python list to be calculated the stddev with
    :param n: sliding window size
    :return: the corresponding std dev
    """
    std = []
    for i , val in enumerate(array):
        batch = array[max(i - n + 1, 0): i + 1]
        std.append(np.std(batch))
    return std


def bbands(array, n=20, k=2):
    """
    Calculate the bollinger band and its derived indicators for a given price array

    :param array: the price array as python list
    :param n: the period considered
    :param k: the ± standard deviation bound range
    :return: the band upper bound, lower bound, %b indicator, and bandwidth
    """
    ma = sma(array, n)
    std = moving_std(array, n)
    ma = np.array(ma)
    std = np.array(std)

    upper = ma + k * std
    lower = ma - k * std
    percent_b = (array - lower) / (upper - lower + 1e-10)
    bandwidth = (upper - lower) / ma

    return upper, lower, percent_b, bandwidth


# aliases
ma = sma


"""Break down of the MACD chart:
    1. Crossovers - As shown in the chart above, when the MACD falls below the signal line,
    it is a bearish signal, which indicates that it may be time to sell. Conversely, when the
    MACD rises above the signal line, the indicator gives a bullish signal, which suggests
    that the price of the asset is likely to experience upward momentum. Many traders wait
    for a confirmed cross above the signal line before entering into a position to avoid
    getting "faked out" or entering into a position too early, as shown by the first arrow.

    2. Divergence - When the security price diverges from the MACD, it signals the end of the
    current trend. For example, a stock price that is rising and a MACD indicator that is
    falling could mean that the rally is about to end. Conversely, if a stock price is falling
    and the MACD is rising, it could mean that a bullish reversal could occur in the near-term.
    Traders often use divergence in conjunction with other technical indicators to find
    opportunities.

    3. Dramatic Rise - When the MACD rises dramatically - that is, the shorter moving average
    pulls away from the longer-term moving average - it is a signal that the security is
    overbought and will soon return to normal levels. Traders will often combine this analysis
    with the Relative Strength Index (RSI) or other technical indicators to verify overbought
    or oversold conditions.
"""

"""The Squeeze
    The squeeze is the central concept of Bollinger Bands®. When the bands come close 
    together, constricting the moving average, it is called a squeeze. A squeeze signals 
    a period of low volatility and is considered by traders to be a potential sign of 
    future increased volatility and possible trading opportunities. Conversely, the 
    wider apart the bands move, the more likely the chance of a decrease in volatility 
    and the greater the possibility of exiting a trade. However, these conditions are 
    not trading signals. The bands give no indication when the change may take place or 
    which direction price could move.

"""
