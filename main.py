import os
from datetime import datetime

from keras.models import load_model

from data.analysis import *
from data.core import load_candlesticks, stack_data, cache, update_recent_candles
from data.synthesize import *
from models import *
from settings import CACHE_ROOT

from matplotlib import pyplot as plt


def synthesize_features(symbol, start, end):
    candles = load_candlesticks(symbol, start, end)
    prices = [cs.close for cs in candles]
    macd, macd_signal, macd_diff = calculate_MACD(prices)
    # bb_upper, bb_lower, percent_b, bandwidth = calculate_bollinger_bands(prices, n=12)
    ma12 = calculate_moving_averages(prices, n=12)
    ma24 = calculate_moving_averages(prices, n=24)
    ma7d = calculate_moving_averages(prices, n=24 * 7)
    flat_data = stack_data(candles, macd, macd_signal, macd_diff, ma12, ma24, ma7d)
    return flat_data


def prepare_data(*symbols):
    start = datetime(2015, 4, 1, 0, 0)
    end = datetime(2018, 5, 1, 0, 0)
    today = datetime.now()

    x_train, y_train = None, None
    x_valid, y_valid = None, None
    for symbol in symbols:
        print("Preparing datasets for {}...".format(symbol))
        train = synthesize_features(symbol, start, end)

        hist_train, fut_train = history2future(train, history_size=72, future_size=6)
        hist_train, fut_train, _, _ = batch_normalize(hist_train, fut_train)
        price_range_train = get_price_range(fut_train)
        direction_train = get_direction(hist_train, fut_train)
        target_train = np.hstack((price_range_train, direction_train))
        x_train = hist_train if x_train is None else np.concatenate((x_train, hist_train))
        y_train = target_train if y_train is None else np.concatenate((y_train, target_train))

        valid = synthesize_features(symbol, end, today)
        hist_valid, fut_valid = history2future(valid, history_size=72, future_size=6)
        hist_valid, fut_valid, _, _ = batch_normalize(hist_valid, fut_valid)
        price_range_valid = get_price_range(fut_valid)
        direction_valid = get_direction(hist_valid, fut_valid)
        target_valid = np.hstack((price_range_valid, direction_valid))
        x_valid = hist_valid if x_valid is None else np.concatenate((x_valid, hist_valid))
        y_valid = target_valid if y_valid is None else np.concatenate((y_valid, target_valid))

    cache(x_train, 'x_train')
    cache(y_train, 'y_train')
    cache(x_valid, 'x_valid')
    cache(y_valid, 'y_valid')


if __name__ == '__main__':

    symbols = ['eos', 'soc', 'btc', 'eth']

    # update_recent_candles('btc', batch_size=2000)
    # scrape_candles('soc', batch_size=2000)
    # prepare_data(*symbols)


    """************ load data from cache files ***********"""
    x = np.load(os.path.join(CACHE_ROOT, 'x_train.npy'))
    y = np.load(os.path.join(CACHE_ROOT, 'y_train.npy'))
    """***************** END *****************"""

    y_range = y[:, 0:2]
    y_momentum = y[:, 2]

    model = future_range_momentum_model(x.shape, 128, .2)
    train_history = model.fit(x, [y_range, y_momentum], epochs=1, batch_size=128, shuffle=True)
    #

    # model = load_model('assets/未来6小时区间模型.h5')
    # model.summary()
