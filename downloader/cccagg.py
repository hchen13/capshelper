import json
import os
from datetime import datetime, timedelta

from downloader.http_utils import *
from settings import ensure_dir_exists

HOST = "https://min-api.cryptocompare.com"

cache_dir = os.path.dirname(__file__) + '/cache'


class CCCAGG(object):
    def __init__(self):
        print("Using CCCAGG as download source")

    def get_coin_list(self, from_cache=False):
        cache_file = 'coins.json'
        cache_path = os.path.join(cache_dir, cache_file)
        ensure_dir_exists(cache_dir)
        if from_cache and os.path.exists(cache_path):
            return json.load(open(cache_path, 'r'))
        response = get_coins()
        json.dump(response, open(cache_path, 'w'))
        return response

    def get_exchanges(self, from_cache=False):
        cache_file = "exchanges.json"
        cache_path = os.path.join(cache_dir, cache_file)
        ensure_dir_exists(cache_dir)
        if from_cache and os.path.exists(cache_path):
            return json.load(open(cache_path, 'r'))
        response = get_exchanges()
        json.dump(response, open(cache_path,'w'))
        return response

    def get_top_coins(self, counter, limit=20):
        print("Downloading top trading coins countered with {}...".format(counter))
        response = get_top_coins(counter, limit)
        coins = [c['ConversionInfo']['CurrencyFrom'] for c in response]
        print("Download complete!\n")
        return coins

    def get_candlesticks(self, base, counter, start, end=None, exchange='CCCAGG'):
        """download the currency pair's OHLCV data between a given period

        :param base: base coin symbol
        :param counter: counter coin symbol
        :param start: starting timestamp
        :param end: ending timestamp
        :param exchange: the exchange from which the data is downloaded
        :return: data in a List
        """
        end = end or datetime.now().timestamp()
        delta = timedelta(seconds=end - start)
        total_hours = int(delta.total_seconds() / 3600) - 1
        batch_size = 2000
        batch_end = datetime.fromtimestamp(start)
        buffer = []
        if not total_hours:
            print("Data is recent, nothing to download.\n")
            return []
        print("Downloading {}/{} candlesticks from {} to {}, {} data in total.".format(
            base, counter,
            datetime.fromtimestamp(start), datetime.fromtimestamp(end),
            total_hours
        ))
        while total_hours > 0:
            length = min(total_hours, batch_size)
            batch_end += timedelta(hours=1) * length
            ts = int(batch_end.timestamp())
            data = get_candlesticks(base, counter, length, ts, exchange)
            buffer += data
            total_hours -= length
            print("Progress: {} left".format(total_hours))
        data = []
        for raw in buffer:
            obj = {
                'base': base,
                'counter': counter,
                'timestamp': raw['time'],
                'open': raw['open'],
                'high': raw['high'],
                'low': raw['low'],
                'close': raw['close'],
                'volume': raw['volumeto']
            }
            data.append(obj)
        print("Download complete!\n")
        return data


def check_limit():
    endpoint = '/stats/rate/limit'
    url = HOST + endpoint
    results = http_get(url)
    second = results.get('Second')
    return json.dumps(second, indent=2)


def get_coins():
    endpoint = "/data/all/coinlist"
    url = HOST + endpoint
    results = http_get(url)
    return results['Data']


def get_exchanges():
    endpoint = "/data/all/exchanges"
    url = HOST + endpoint
    results = http_get(url)
    return results


def get_candlesticks(base, counter, length, end, exchange):
    """request API for candlesticks data

    :param base: base coin
    :param counter: counter coin
    :param length: number of candlesticks for which the user asks
    :param end: the candlesticks ending in this time, represented in timestamp
    :param exchange: the exchange from which the data is downloaded
    :return: candlesticks in List
    """
    base = base.upper()
    counter = counter.upper()
    endpoint = '/data/histohour'
    params = {
        'fsym': base,
        'tsym': counter,
        'limit': length,
        'e': exchange,
        'toTs': end
    }
    url = HOST + endpoint
    response = http_get(url, params)
    if 'Data' not in response:
        import sys
        sys.stderr.write("Invalid request...\n")
        return response
    data = response['Data']
    return data[:-1]


def get_top_coins(counter, limit=20):
    counter = counter.upper()
    endpoint = '/data/top/totalvol'
    params = {
        'limit': limit,
        'tsym': counter
    }
    url = HOST + endpoint
    response = http_get(url, params)
    if 'Data' not in response:
        import sys
        sys.stderr.write("Invalid request...\n")
        return response
    data = response['Data']
    return data
