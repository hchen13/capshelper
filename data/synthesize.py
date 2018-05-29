"""
This module contains methods to synthesize various forms of datasets
for training
"""
import numpy as np

def history2future(flat_data, history_size, future_size=1):
    """Stack <history_size> historical data together as inputs and for each input,
    output its corresponding <future_size> historical data happened right after that.
    The method synthesizes datasets used for training models to predict the future with
    previous data.

    :param flat_data: flattened data of the candlesticks for a time series
    :param history_size: the number of previous historical data stacked together
    :param future_size: the number of historical data in the future stacked together
    :return: x and y in numpy ndarrays.
    x shape (m, <history_size>, n), y shape (m, <future_size>, n)
    where m denotes the number of examples,
    n denotes the number of features for one set of time series data, e.g. OCHLV + EMA + MACD
    """
    data_size = len(flat_data)
    x, y = [], []
    window_size = history_size + future_size
    for i in range(data_size - window_size + 1):
        inputs = flat_data[i : i + history_size]
        outputs = flat_data[i + history_size : i + window_size]
        x.append(inputs)
        y.append(outputs)

    return np.array(x), np.array(y)


def batch_normalize(history, future):
    """
    batch normalize the history matrices into [0, 1] and use same params
    to normalize the future matrices, not necessarily in [0, 1]
    :param history: the history array of shape (m, history_size, n)
    :param future:  the future array of shape (m, future_size, n)
    :return: normalized history x and future y, along with upper and lower for denorm
    """
    upper = history.max(axis=1, keepdims=True)
    lower = history.min(axis=1, keepdims=True)
    x = (history - lower) / (upper - lower + 1e-8)
    y = (future - lower) / (upper - lower + 1e-8)
    return x, y, upper, lower


def get_price_range(array):
    closing_prices = array[:, :, 3]
    peaks = closing_prices.max(axis=1, keepdims=True)
    valleys = closing_prices.min(axis=1, keepdims=True)
    y = np.hstack((peaks, valleys))
    return y


def get_direction(past, future):
    base_price = past[:, -1, 3]
    last_price = future[:, -1, 3]
    return np.reshape(last_price - base_price, (-1, 1))