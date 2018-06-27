from datetime import datetime

from matplotlib import pyplot as plt


def draw_sample(past, future):
    fig, (top, bot) = plt.subplots(2, 1, gridspec_kw={"height_ratios": [3, 1]}, figsize=[16, 9])

    t1 = [datetime.fromtimestamp(x) for x in past['timestamp']]
    t2 = [datetime.fromtimestamp(x) for x in future['timestamp']]
    t = t1 + t2

    # draw prices
    top.plot(t1, past['close'], 'b')
    top.plot(t2, future['close'], 'b--')
    # draw ma6
    top.plot(t1, past['ma1'], 'k', linewidth=.6, label='ma 6')
    top.plot(t2, future['ma1'], 'k--', linewidth=.6, label='ma 6')
    # draw ma12
    top.plot(t1, past['ma2'], 'g', linewidth=.6, label='ma 12')
    top.plot(t2, future['ma2'], 'g--', linewidth=.6, label='ma 12')
    # draw ma24
    top.plot(t1, past['ma3'], 'r', linewidth=.6, label='ma 24')
    top.plot(t2, future['ma3'], 'r--', linewidth=.6, label='ma 24')

    # draw MACD
    bot.plot(t1, past['macd_proper'], 'k', linewidth=1, label='MACD')
    bot.plot(t2, future['macd_proper'], 'k--', linewidth=1, label='MACD')
    # draw MACD signal
    bot.plot(t1, past['macd_signal'], 'r', linewidth=1, label='signal')
    bot.plot(t2, future['macd_signal'], 'r--', linewidth=1, label='signal')
    # draw MACD diff
    bot.fill_between(t1, past['macd_diff'], 0)
    bot.fill_between(t2, future['macd_diff'], 0)

    top.legend()
    bot.legend()
    plt.tight_layout()
    plt.show()