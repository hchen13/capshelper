import datetime
import json

from backend.cryptocompare import get_coins, get_candlesticks
from backend.utils import timestamp2time
from data.db import init_db, Coin, Candlestick
from settings import *
from data.analysis import *


Session = init_db()


def update_coins(from_cache=False):
    session = Session()
    if from_cache:
        cache_file = os.path.join(ROOT_DIR, 'coins.json')
        with open(cache_file, 'r') as cache:
            d = json.load(cache)
    else:
        d = get_coins()

    if d is None:
        print("Updating failed: Error while extracting coin information.")
        return

    print("Updading coin information in the database...")
    for key, val in d.items():
        symbol = val['Symbol']
        attrs = {
            'algorithm': val['Algorithm'],
            'coin_name': val['CoinName'],
            'fullname': val['FullName'],
            'id': val['Id'],
            'image_url': 'https://https://www.cryptocompare.com' + val['ImageUrl'] if 'ImageUrl' in val else None,
            'name': val['Name'],
            'symbol': val['Symbol'],
            'url': 'https://www.cryptocompare.com' + val['Url']
        }
        queryset = session.query(Coin).filter(Coin.symbol == symbol)
        if queryset.count():
            queryset.update(attrs)
        else:
            coin = Coin(**attrs)
            session.add(coin)
    session.commit()
    print("Updating complete!\n")


def data_ends(data):
    if not len(data):
        return True
    first = data[0]
    o, h, l, c = first['open'], first['high'], first['low'], first['close']
    volume = first['volumefrom']
    if o == h == l == c == volume == 0:
        return True
    return False


def scrape_candles(symbol, batch_size=100):
    """Download all candlestick data for a given symbol, prices are represented as USD

    :param symbol: a string such as 'utc'
    :param batch_size: batch size for one download request
    :return: None
    """
    bench = 'usd'
    delta = datetime.timedelta(hours=1)

    print("Downloading the most recent batch of candlesticks of `{}`...".format(symbol))
    batch = get_candlesticks(symbol, bench, length=batch_size)
    print("Download complete!\n")

    save_candles(symbol, batch, bench)

    while True:
        start_timestamp = batch[0]['time']
        start_time = timestamp2time(start_timestamp)
        end_time = start_time - delta
        print("Downloading the candlesticks of `{}` ending at {}...".format(symbol, end_time))
        batch = get_candlesticks(symbol, bench, length=batch_size, end=end_time)
        print("Download complete!\n")
        save_candles(symbol, batch, bench)
        if data_ends(batch):
            break

    print("All candlesticks of `{}` are saved.\n".format(symbol))


def update_recent_candles(symbol, batch_size=24):
    """Update missing candlestick data until all caught up

    :param symbol: a string such as 'utc'
    :param batch_size: batch size
    :return: None
    """
    bench = 'usd'
    delta = datetime.timedelta(hours=1)

    print("Downloading the most recent batch of candlesticks of `{}`...".format(symbol))
    batch = get_candlesticks(symbol, bench, length=batch_size)
    print("Download complete!\n")

    added = save_candles(symbol, batch, bench)

    while added:
        start_timestamp = batch[0]['time']
        start_time = timestamp2time(start_timestamp)
        end_time = start_time - delta
        print("Downloading the candlesticks of `{}` ending at {}...".format(symbol, end_time))
        batch = get_candlesticks(symbol, bench, length=batch_size, end=end_time)
        print("Download complete!\n")
        added = save_candles(symbol, batch, bench)

    print("All recent candlesticks of `{}` are saved.\n".format(symbol))


def save_candles(symbol, data, bench):
    """Saving the data into the database"""
    print("Saving {} candles into the database...".format(len(data)))

    symbol = symbol.upper()
    session = Session()

    added = 0

    for i, raw in enumerate(data):

        if i % 100 == 0:
            print("Progress: {:.2f}%".format(i / len(data) * 100))

        queryset = session.query(Candlestick).filter(
            Candlestick.coin_symbol == symbol,
            Candlestick.timestamp == raw['time']
        )
        if queryset.count():
            continue

        record = Candlestick(
            coin_symbol=symbol,
            timestamp=raw['time'],
            time=timestamp2time(raw['time']),
            open=raw['open'],
            close=raw['close'],
            high=raw['high'],
            low=raw['low'],
            volume=raw['volumefrom'],
            bench=bench
        )
        session.add(record)
        added += 1

    session.commit()

    print("Saving complete! {} new records saved.\n".format(added))
    return added


def load_candlesticks(symbol, start=None, end=None):
    if start is None:
        start = datetime.datetime(2011, 1, 1, 0, 0)
    if end is None:
        end = datetime.datetime.now()
    session = Session()
    queryset = session.query(Candlestick).filter(
        Candlestick.coin_symbol == symbol,
        Candlestick.time >= start,
        Candlestick.time <= end
    ).order_by(Candlestick.timestamp)
    return queryset.all()


def load_matrix(symbol, start=None, end=None):
    if start is None:
        start = datetime.datetime(2011, 1, 1, 0, 0)
    if end is None:
        end = datetime.datetime.now()
    candles = load_candlesticks(symbol, start, end)
    mat = np.array([cs.as_vector() for cs in candles])
    return mat


def load_dataset(symbol, window_size=72, start=None, end=None):
    candles = load_candlesticks(symbol, start, end)
    size = len(candles)
    x = []
    y = []
    for i in range(window_size, size):
        batch = candles[i - window_size : i]
        label = candles[i].as_vector()
        data = [cs.as_vector() for cs in batch]
        x.append(data)
        y.append(label)
    x = np.array(x)
    y = np.array(y)
    return x, y


def cache(ndarray, filename):
    path = os.path.join(CACHE_ROOT, filename)
    ensure_dir_exists(CACHE_ROOT)
    np.save(path, ndarray)


def create_dataset(candlesticks, window_size, *indicators):
    data_size = len(candlesticks)
    # check if all the extra indicators share the same data length
    for indicator in indicators:
        assert len(indicator) == data_size

    flat_data = []
    x, y = [], []
    for i in range(data_size):
        candle = candlesticks[i]
        main_vector = candle.as_vector()
        for indicator in indicators:
            val = indicator[i]
            main_vector = np.append(main_vector, val)
        flat_data.append(main_vector)

    # stack every <window_size> data together to form a matrix
    # representing the change over <window_size> hours
    for i in range(window_size, data_size):
        batch = flat_data[i - window_size : i]
        label = flat_data[i]
        x.append(batch)
        y.append(label)

    x = np.array(x)
    y = np.array(y)

    return x, y


if __name__ == '__main__':
    # update_recent_candles('btc', batch_size=2000)

    candles = load_candlesticks('btc', start=datetime.datetime(2018, 4, 1, 0, 0))
    prices = [cs.close for cs in candles]
    ma5 = calculate_moving_averages(prices, n=5)
    std5 = calculate_moving_std(prices, n=20)
    bb_upper, bb_lower, pb, bw = calculate_bollinger_bands(prices, n=20, k=2)
    ema5 = calculate_exponentially_moving_averages(prices, n=5)
    macd, macd_signal, macd_diff = calculate_MACD(prices)
    ema10 = calculate_exponentially_moving_averages(prices, n=10)


    timeline = [cs.time for cs in candles]

    from matplotlib import pyplot as plt

    plt.figure(figsize=(21, 3))
    plt.plot(timeline, prices, 'k')
    plt.show()