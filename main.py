from datetime import datetime

import os

from data.analysis import *
from data.core import cache, load_candlesticks, create_dataset
from models import single_price_model
from settings import CACHE_ROOT


def prepare_data(symbol, start, end):
    candles = load_candlesticks(symbol, start, end)
    prices = [cs.close for cs in candles]
    macd, macd_signal, macd_diff = calculate_MACD(prices)
    # bb_upper, bb_lower, percent_b, bandwidth = calculate_bollinger_bands(prices, n=12)
    ma12 = calculate_moving_averages(prices, n=12)
    ma24 = calculate_moving_averages(prices, n=24)
    ma7d = calculate_moving_averages(prices, n=24 * 7)
    x, y = create_dataset(candles, 72, macd, macd_signal, macd_diff, ma12, ma24, ma7d)
    y = y[:, 3]
    return x, y


if __name__ == '__main__':

    """prepare the datasets for training and testing"""
    # start = datetime(2016, 1, 1, 0, 0)
    # end = datetime(2018, 5, 1, 0, 0)
    # today = datetime.now()
    # x, y = prepare_data('btc', start, end)
    # cache(x, 'x_train')
    # cache(y, 'y_train')
    # x_test, y_test = prepare_data('btc', end, today)
    # cache(x_test, 'x_test')
    # cache(y_test, 'y_test')
    """************** END *****************"""

    """************ load data from cache files ***********"""
    x = np.load(os.path.join(CACHE_ROOT, 'x_train.npy'))
    y = np.load(os.path.join(CACHE_ROOT, 'y_train.npy'))
    """***************** END *****************"""

    model = single_price_model(x.shape, 1024, .5)
    train_history = model.fit(x, y, epochs=10, batch_size=128, shuffle=False)

    x_ = np.load(os.path.join(CACHE_ROOT, 'x_test.npy'))
    y_ = np.load(os.path.join(CACHE_ROOT, 'y_test.npy'))
    predictions = model.predict(x_)
