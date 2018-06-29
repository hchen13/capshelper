import os
import sys
from datetime import datetime, timedelta

import pandas as pd
from pandas import DataFrame
from sqlalchemy import desc

from butler.db import *
from butler.indicators import *
from settings import ensure_dir_exists

DEFAULT_DATABASE = {
    'host': "localhost",
    'name': "cccagg",
    "user": 'root',
    'pwd': 'root'
}


class _Butler:
    """
    The Butler manages and manipulates the database. A butler can save and retrieve data
    from the database upon request, and identify invalid data
    """
    def __init__(self, db_configs=None):
        if db_configs is None:
            db_configs = DEFAULT_DATABASE
        self.Session = init_db(**db_configs)

    def check_db_integrity(self, base, counter):
        """Checks the data integrity of a given coin pair. False when candlesticks are not hourly coherent
        or indicators not calculated

        :param base: base coin
        :param counter: counter coin
        :return: boolean, indicating whether the pair is in good shape
        """
        standard = timedelta(hours=1)
        candles = self.retrieve_candlesticks(base, counter)
        for i, c in enumerate(candles):
            if i == 0:
                continue
            last = candles[i - 1]
            t0 = last['timestamp']
            t1 = c['timestamp']
            delta = t1 - t0
            if standard.total_seconds() != delta:
                return False
            if c['ma1'] is None:
                return False
        return True

    def all_pairs(self):
        """Summarize all the existing coin pairs and the number of corresponding
        candlesticks data currently stored in the database

        :return:
        """
        session = self.Session()
        pairs = session.query(Candlestick.base, Candlestick.counter).distinct().all()
        results = []
        for base, counter in pairs:
            count = session.query(Candlestick).filter(
                Candlestick.base == base,
                Candlestick.counter == counter
            ).count()
            obj = {
                'pair': (base, counter),
                'count': count
            }
            results.append(obj)
        return sorted(results, key=lambda x: x['count'], reverse=True)


    def valid_candlestick(self, data):
        """Validate the candlestick data and identify valid ones

        :param data: single candlestick data in the same format as `save_candlesticks`
        :return: True if valid else False
        """
        for key in ['open', 'close', 'high', 'low', 'volume']:
            value = data[key]
            if value != 0:
                return True
        return False

    def save_candlesticks(self, data):
        """Save given candlesticks data into the database, each candlestick data has to
        be in the following format:
        {
            "base": "btc",
            "counter": "eth",
            "open": X.X,
            "close": X.X,
            "high": X.X,
            "low": X.X,
            "volume": X.X
        }

        :param data: list of candlesticks data
        :return: None
        """
        session = self.Session()
        added = 0
        updated = 0
        print("Saving candlestick data into database...")
        for i, obj in enumerate(data):
            progress = i / len(data) * 100
            if progress % 10 - 0 < 1e-2:
                print("Progress: {:.2f}%".format(progress))
            if not self.valid_candlestick(obj):
                continue
            queryset = session.query(Candlestick).filter(
                Candlestick.base == obj['base'],
                Candlestick.counter == obj['counter'],
                Candlestick.timestamp == obj['timestamp']
            )
            if queryset.count() == 0:
                time = datetime.fromtimestamp(obj['timestamp'])
                record = Candlestick(**obj, time=time)
                session.add(record)
                added += 1
            else:
                queryset.update(obj)
                updated += 1
        print("Progress: 100%")
        session.commit()
        print("Saving complete! {} new records saved.\n".format(added))
        return added

    def retrieve_candlesticks(self, base, counter, start=None, end=None):
        """Retrieve candlestick data from the database

        :param base: base coin
        :param counter: counter coin
        :param start: starting timestamp
        :param end: ending timestamp, defaults to None (current time)
        :return: List of candlesticks
        """
        print("Retrieving data from the database...")
        base = base.upper()
        counter = counter.upper()
        session = self.Session()

        queryset = session.query(Candlestick).filter(
            Candlestick.base == base,
            Candlestick.counter == counter,
        ).order_by(Candlestick.timestamp)
        if start is not None:
            queryset = queryset.filter(Candlestick.timestamp >= start)
        if end is not None:
            queryset = queryset.filter(Candlestick.timestamp <= end)
        queryset = queryset.all()
        print("{} candlesticks for {}/{} retrieved.\n".format(len(queryset), base, counter))
        return [candle.to_representation() for candle in queryset]

    def update_indicators(self, base, counter):

        def update_db_instance(instance, ma1, ma2, ma3, mp, ms, md):
            # if instance.ma1 != ma1:
                instance.ma1 = ma1
            # if instance.ma2 != ma2:
                instance.ma2 = ma2
            # if instance.ma3 != ma3:
                instance.ma3 = ma3
            # if instance.macd_proper != mp:
                instance.macd_proper = mp
            # if instance.macd_signal != ms:
                instance.macd_signal = ms
            # if instance.macd_diff != md:
                instance.macd_diff = md

        candlesticks = self.retrieve_candlesticks(base, counter)
        prices = [c['close'] for c in candlesticks]

        print("Calculating extra indicators...")
        ma6 = sma(prices, 6)
        ma12 = sma(prices, 12)
        ma24 = sma(prices, 24)
        macd_proper, macd_signal, macd_diff = macd(prices)

        print("Calculation complete, updating database...")
        session = self.Session()
        for i, candle in enumerate(candlesticks):
            progress = i / len(candlesticks) * 100
            if progress % 10 - 0 < 1e-2:
                print("Progress: {:.2f}%".format(progress))
            if candle['ma1'] is not None:
                continue
            id = int(candle['id'])
            new_candle = session.query(Candlestick).filter(Candlestick.id == id).one()
            update_db_instance(
                new_candle, ma6[i], ma12[i], ma24[i],
                macd_proper[i], macd_signal[i], macd_diff[i]
            )
        print("Progress: 100%")
        session.commit()
        print("Update complete!\n")

    def as_dataframe(self, candlesticks):
        df = DataFrame(candlesticks)
        return df.drop(columns=['id', 'base', 'counter', 'time'])

    def generate_past_future_pair(self, candlesticks, past_length=72, future_length=12, norm=True):
        print("Creating past({})-future({}) pairs from given candlesticks...".format(past_length, future_length))
        df = self.as_dataframe(candlesticks)
        data_size = len(df)
        x, y = [], []
        window_size = past_length + future_length
        for i in range(data_size - window_size + 1):

            progress = (i + 1) / (data_size - window_size + 1) * 100
            if int(progress) % 20 == 0 and progress - int(progress) < 1e-2:
                print("Progress: {:.2f}%".format(progress))

            inputs = df.iloc[i : i + past_length]
            outputs = df.iloc[i + past_length : i + window_size]
            if norm:
                inputs, outputs = self.normalize_pair(inputs, outputs)
            x.append(inputs)
            y.append(outputs)
        print("Creation complete!\n")
        return x, y

    def normalize_pair(self, past, future):
        merged = pd.concat([past, future])

        mean = merged['close'].mean()
        std = merged['close'].std()
        merged['open'] = (merged['open'] - mean) / (std + 1e-6)
        merged['close'] = (merged['close'] - mean) / (std + 1e-6)
        merged['high'] = (merged['high'] - mean) / (std + 1e-6)
        merged['low'] = (merged['low'] - mean) / (std + 1e-6)
        merged['ma1'] = (merged['ma1'] - mean) / (std + 1e-6)
        merged['ma2'] = (merged['ma2'] - mean) / (std + 1e-6)
        merged['ma3'] = (merged['ma3'] - mean) / (std + 1e-6)

        mean = merged['volume'].mean()
        std = merged['volume'].std()
        merged['volume'] = (merged['volume'] - mean) / (std + 1e-6)

        # macds = merged[['macd_proper', 'macd_signal', 'macd_diff']]
        mean = merged['macd_proper'].mean()
        std = merged['macd_proper'].std()
        merged['macd_proper'] = (merged['macd_proper'] - mean) / (std + 1e-6)
        merged['macd_signal'] = (merged['macd_signal'] - mean) / (std + 1e-6)
        merged['macd_diff'] = merged['macd_proper'] - merged['macd_signal']

        x = merged.iloc[:len(past)]
        y = merged.iloc[len(past):]
        return x, y

    def as_train_data(self, past, future):
        mat_past = [p.values for p in past]
        mat_future = [f.values for f in future]
        return mat_past, mat_future

    def cache(self, tensor, path):
        ensure_dir_exists(os.path.dirname(path))
        print("Caching data or shape {}...".format(tensor.shape))
        np.save(path, tensor)

    def latest_timestamp(self, base, counter):
        session = self.Session()
        latest = session.query(Candlestick).filter(
            Candlestick.base == base,
            Candlestick.counter == counter
        ).order_by(desc(Candlestick.timestamp)).first()
        if latest is None:
            sys.stderr.write("No {}/{} data in the database\n".format(base, counter))
            return None
        return latest.timestamp

    def generate_train_files(self, path, suffix, start=None, end=None):
        pairs = self.all_pairs()
        total_count = 0
        x, y = [], []
        for i in pairs:
            if total_count > 1_000_000:
                break
            total_count += i['count']
            base, counter = i['pair']
            candlesticks = self.retrieve_candlesticks(base, counter, start, end)
            past, future = self.generate_past_future_pair(candlesticks, 72, 12, norm=True)
            inputs, outputs = self.as_train_data(past, future)
            x += inputs
            y += outputs
        x = np.array(x)
        y = np.array(y)
        self.cache(x, os.path.join(path, 'x_{}.npy'.format(suffix)))
        self.cache(y, os.path.join(path, 'y_{}.npy'.format(suffix)))
