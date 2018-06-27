import urllib
from datetime import datetime, timedelta

from pandas import DataFrame
import pandas as pd

from butler import Butler
from butler.indicators import *
from butler.visualize import *
from downloader import *


butler = Butler()
downloader = Downloader()


def initial(base, counter):
    start_date = datetime(2017, 2, 1, 0, 0)
    data = downloader.get_candlesticks(base, counter, start=start_date.timestamp())
    butler.save_candlesticks(data)
    butler.update_indicators(base, counter)


if __name__ == '__main__':
    # initial('btc', 'usdt')

    # experiments
    base, counter = 'btc', 'usdt'
    past, future = butler.generate_past_future_pair(base, counter)

    x, y = past[-1], future[-1]
    xn, yn = butler.normalize(x, y)

    draw_sample(x, y)
    # draw_sample(xn, yn)
