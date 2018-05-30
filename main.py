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
    ma12 = calculate_moving_averages(prices, n=12)
    ma24 = calculate_moving_averages(prices, n=24)
    ma7d = calculate_moving_averages(prices, n=24 * 7)
    flat_data = stack_data(candles, macd, macd_signal, macd_diff, ma12, ma24, ma7d)

    return flat_data


def prepare_data(*symbols, history_size=72, future_size=1):
    start = datetime(2015, 4, 1, 0, 0)
    end = datetime(2018, 5, 1, 0, 0)
    today = datetime.now()

    x_train, y_train = None, None
    x_valid, y_valid = None, None
    for symbol in symbols:
        print("Preparing datasets for {}...".format(symbol))
        train = synthesize_features(symbol, start, end)

        hist_train, fut_train = history2future(train, history_size=history_size, future_size=future_size)
        hist_train, fut_train, _, _ = batch_normalize(hist_train, fut_train)

        direction_train = get_direction(hist_train, fut_train)
        price_train = get_closing_price(fut_train)
        target_train = np.hstack((price_train, direction_train))
        x_train = hist_train if x_train is None else np.concatenate((x_train, hist_train))
        y_train = target_train if y_train is None else np.concatenate((y_train, target_train))

        valid = synthesize_features(symbol, end, today)
        hist_valid, fut_valid = history2future(valid, history_size=history_size, future_size=future_size)
        hist_valid, fut_valid, _, _ = batch_normalize(hist_valid, fut_valid)

        direction_valid = get_direction(hist_valid, fut_valid)
        price_valid = get_closing_price(fut_valid)
        target_valid = np.hstack([price_valid, direction_valid])
        x_valid = hist_valid if x_valid is None else np.concatenate([x_valid, hist_valid])
        y_valid = target_valid if y_valid is None else np.concatenate([y_valid, target_valid])

    cache(x_train, 'x_train')
    cache(y_train, 'y_train')
    cache(x_valid, 'x_valid')
    cache(y_valid, 'y_valid')


if __name__ == '__main__':

    symbols = ['eos', 'soc', 'btc', 'eth']

    # for symbol in symbols:
    #     update_recent_candles(symbol, batch_size=2000)

    # prepare_data(*symbols, history_size=72, future_size=1)


    """************ load data from cache files ***********"""
    x = np.load(os.path.join(CACHE_ROOT, 'x_train.npy'))
    y = np.load(os.path.join(CACHE_ROOT, 'y_train.npy'))
    """***************** END *****************"""
    #
    y_price = y[:, 0]
    y_direction = y[:, 1] > 0

    model = next_price_direction_model(x.shape, 128, .2)
    train_history = model.fit(x, [y_price, y_direction], epochs=1, batch_size=128, shuffle=True)
    # # #
    # x_ = np.load(os.path.join(CACHE_ROOT, 'x_valid.npy'))
    # y_ = np.load(os.path.join(CACHE_ROOT, 'y_valid.npy'))
    # true_direction = y_[:, 2] > 0
    # #
    # print("input shape: ", x_.shape)
    # print("target shape:", true_direction.shape)
    # #
    # performance = model.evaluate(x_, true_direction)
    # for i, metric in enumerate(model.metrics_names):
    #     print("{}: {:.4f}".format(metric, performance[i]))
