from datetime import datetime

from matplotlib import pyplot as plt

from data.core import load_candlesticks


def display_price_line(symbol, start, end):
    dataset = load_candlesticks(symbol, start, end)
    x = [cs.time for cs in dataset]
    y = [cs.close for cs in dataset]
    plt.title(symbol + " price")
    plt.plot(x, y, 'k')
    plt.show()


def display_volume(symbol, start, end):
    dataset = load_candlesticks(symbol, start, end)
    x = [cs.time for cs in dataset]
    y = [cs.volume for cs in dataset]
    plt.title(symbol + ' volume')
    plt.bar(x, y, .02)
    plt.show()


def display(symbol, start, end):
    dataset = load_candlesticks(symbol, start, end)
    x = [cs.time for cs in dataset]
    p = [cs.close for cs in dataset]
    v = [cs.volume for cs in dataset]

    fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})

    ax1.set_ylabel('Closing Price ($)', fontsize=8)
    ax2.set_ylabel('Volume ($)', fontsize=8)

    ax2.set_yticks([i for i in range(10)])
    ax2.set_yticklabels(range(10))

    ax1.plot(x, p)
    ax2.bar(x, v, .02)
    fig.tight_layout()
    plt.show()


def main():
    start_time = datetime(2018, 5, 10, 0, 0)
    end_time = datetime.now()
    display('btc', start_time, end_time)


if __name__ == '__main__':
    main()
