import json
import os
from urllib.parse import urlencode
from datetime import datetime

import pytz
import requests

from backend.utils import timestamp2time

HOST = "https://min-api.cryptocompare.com"
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


def _http_get(url, params=None):
    encoded = urlencode(params if params else {})
    try:
        response = requests.get(url, encoded, timeout=10)
    except BaseException as e:
        print("Error while sending request: {}".format(e))
        return None
    if response.status_code == 200:
        return response.json()
    print("Request failed with code {}, detail: {}".format(response.status_code, response.text))
    return None


def get_coins(cache=False):
    print("Loading coins from www.cryptocompare.com...")
    endpoint = 'data/all/coinlist'
    url = os.path.join(HOST, endpoint)
    results = _http_get(url)
    if results is None:
        return None
    if cache:
        with open(os.path.join(ROOT_DIR, 'coins.json'), 'w') as cache:
            json.dump(results['Data'], cache)
    print("Loading complete!\n")
    return results['Data']


def get_exchanges(cache=False):
    endpoint = "data/all/exchanges"
    url = os.path.join(HOST, endpoint)
    results = _http_get(url)
    if results is None:
        return None
    if cache:
        with open(os.path.join(ROOT_DIR, 'exchanges.json'), 'w') as cache:
            json.dump(results, cache)
    return results


def get_price(symbol, benchmark='CNY', market='CCCAGG'):
    """
    Get the current price of any cryptocurrency in any other currency that you need.

    :param symbol:
    :param benchmark:
    :param market:
    :return:
    """
    endpoint = 'data/price'
    if type(benchmark) == list:
        bench = ','.join([s.upper() for s in benchmark])
    else:
        bench = benchmark.upper()
    params = {
        'fsym': symbol.upper(),
        'tsyms': bench,
        'e': market
    }
    url = os.path.join(HOST, endpoint)
    results = _http_get(url, params)
    if results is None:
        return None
    return results


def get_current_average(symbol, bench='CNY', market='CCCAGG'):
    """
    Compute the current trading info of the requested symbol

    :param symbol: the currency would like to checkout with
    :param bench: the benchmarking currency to see the price with
    :param market: the market the info comes from
    :return:
    """
    endpoint = 'data/generateAvg'
    symbol = symbol.upper()
    bench = bench.upper()
    params = {
        "fsym": symbol,
        "tsym": bench,
        "e": market
    }
    url = os.path.join(HOST, endpoint)
    results = _http_get(url, params)
    if results is None:
        return None
    data = results['RAW']
    return data


def get_candlesticks(symbol, bench='CNY', length=100, end=None, interval='hour', market='CCCAGG'):
    interval = interval.lower()
    symbol = symbol.upper()
    bench = bench.upper()
    endpoint = 'data/histo{}'.format(interval)
    params = {
        'fsym': symbol,
        'tsym': bench,
        'limit': length - 1,
        'e': market
    }
    if end:
        params['toTs'] = end.timestamp()

    url = os.path.join(HOST, endpoint)
    results = _http_get(url, params)
    if results is None:
        return None
    data = results['Data']
    return data


if __name__ == '__main__':
    pass
