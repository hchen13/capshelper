import os
from datetime import datetime

from data.analysis import *
from data.core import load_candlesticks, stack_data, cache
from data.synthesize import *
from models import future_range_model
from settings import CACHE_ROOT


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

        hist_train, fut_train = history2future(train, history_size=72, future_size=24)
        x_train_batch, y_train_batch = synthesize_past_future_dataset(hist_train, fut_train)
        x_train = np.concatenate((x_train, x_train_batch), axis=0) if x_train is not None else x_train_batch
        y_train = np.concatenate((y_train, y_train_batch), axis=0) if y_train is not None else y_train_batch

        valid = synthesize_features(symbol, end, today)
        hist_valid, fut_valid = history2future(valid, history_size=72, future_size=24)
        x_valid_batch, y_valid_batch = synthesize_past_future_dataset(hist_valid, fut_valid)
        x_valid = np.concatenate((x_valid, x_valid_batch), axis=0) if x_valid is not None else x_valid_batch
        y_valid = np.concatenate((y_valid, y_valid_batch), axis=0) if y_valid is not None else y_valid_batch


    cache(x_train, 'x_train')
    cache(y_train, 'y_train')
    cache(x_valid, 'x_valid')
    cache(y_valid, 'y_valid')


if __name__ == '__main__':

    # update_recent_candles('btc', batch_size=2000)
    # scrape_candles('soc', batch_size=2000)
    # prepare_data('eos', 'soc', 'btc', 'eth')


    """************ load data from cache files ***********"""
    x = np.load(os.path.join(CACHE_ROOT, 'x_train.npy'))
    y = np.load(os.path.join(CACHE_ROOT, 'y_train.npy'))
    """***************** END *****************"""

    #
    model = future_range_model(x.shape, 64, .5)
    train_history = model.fit(x, y, epochs=1, batch_size=128, shuffle=True)
    #
    # x_ = np.load(os.path.join(CACHE_ROOT, 'x_test.npy'))
    # y_ = np.load(os.path.join(CACHE_ROOT, 'y_test.npy'))
    # predictions = model.predict(x_)
    # model.evaluate(x_, y_)