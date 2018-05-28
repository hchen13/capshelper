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


def synthesize_past_future_dataset(history, future):
    # [0, 1] normalization
    upper = history.max(axis=1, keepdims=True)
    lower = history.min(axis=1, keepdims=True)
    x = (history - lower) / (upper - lower + 1e-8)
    future_norm = (future - lower) / (upper - lower + 1e-8)

    closing_prices = future_norm[:, :, 3]
    peaks = closing_prices.max(axis=1, keepdims=True)
    valleys = closing_prices.min(axis=1, keepdims=True)
    y = np.hstack((peaks, valleys))

    return x, y