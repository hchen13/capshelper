import json
import os

from butler import Butler
from butler.visualize import *
from downloader import *
from settings import ROOT_DIR

butler = Butler()
downloader = Downloader()

main_coins = 'USDT BTC ETH'.split(" ")


def update_watchlist():
    watchlist = []
    for counter in main_coins:
        coins = downloader.get_top_coins(counter, limit=20)
        watchlist += coins
    return list(set(watchlist))


def get_watchlist(from_cache=True):
    cache_file = "watchlist.json"
    cache_path = os.path.join(ROOT_DIR, cache_file)
    if from_cache and os.path.exists(cache_path):
        return json.load(open(cache_path, 'r'))
    watchlist = update_watchlist()
    json.dump(watchlist, open(cache_path, 'w'))
    return watchlist


def collect(base, counter):
    base = base.upper()
    counter = counter.upper()
    ts = butler.latest_timestamp(base, counter)
    if ts is None:
        ts = datetime(2017, 2, 1, 0, 0).timestamp()
    data = downloader.get_candlesticks(base, counter, start=ts)
    if len(data):
        butler.save_candlesticks(data)
    butler.update_indicators(base, counter)


def single_run():
    watchlist = get_watchlist(from_cache=True)
    for counter in main_coins:
        for base in watchlist:
            counter = counter.upper()
            base = base.upper()
            if base == counter:
                continue
            collect(base, counter)


def prepare_train_data(path):
    train_end = datetime(2018, 6, 1, 23, 59).timestamp()
    valid_end = datetime(2018, 6, 10, 23, 59).timestamp()
    test_end = datetime.now().timestamp()
    butler.generate_train_files(path, 'train', end=train_end)
    butler.generate_train_files(path, 'valid', start=train_end + 1, end=valid_end)
    butler.generate_train_files(path, 'test', start=valid_end + 1, end=test_end)


if __name__ == '__main__':
    # get_watchlist(False)
    # single_run()
    prepare_train_data('data/')
