import glob
import math
import os
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import src.constants as c

DATASET_DIR = './dataset/mail/uncompressed'

def start():
    plotMessagesPerMonth(parseMailArchive(), c.CHARTS_DIR + '/mail_msg-per-month.png')

    #plt.show()


def plotMessagesPerMonth(df, fpath):
    maxMsgCount= df['MSG_COUNT'].max()
    vLineColor = c.PALETTE[3]
    barColor = c.PALETTE[2]

    meanPerYear = df.groupby(df.MONTH.dt.year)['MSG_COUNT'].agg(['mean'])
    meanPerMonth = math.ceil(df['MSG_COUNT'].mean())

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'
    plt.rc('axes', axisbelow=True)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(100))
    ax.grid(True, axis='both')

    plt.ylabel('Message Count')
    plt.ylim(0, maxMsgCount + 50)

    # two charts on a single plot
    line = sns.lineplot(x=df['MONTH'], y=df['MSG_COUNT'], ax=ax)
    ax.bar(pd.to_datetime(
        meanPerYear.index, format='%Y'), meanPerYear['mean'],
        width=365, alpha=0.5, color=barColor, align='edge'
    )

    plt.xlabel(None)
    line.set(xlabel=None)
    plt.title('Mailing List Activity', pad=16)

    # annotate
    plt.vlines(x=c.RELEASES.values(), ymin=0, ymax=maxMsgCount, color=vLineColor, alpha=0.8, linestyles='dotted')
    for i, x in enumerate(c.RELEASES.values()):
        plt.text(x, maxMsgCount + 10, 'v%d' % (19 - i), va='center', ha='center', alpha=0.8, fontsize='small')

    plt.text(
        datetime(2017, 1, 1), 500, '{} messages per month'.format(meanPerMonth), fontsize=12, ha='center', va='center',
        bbox=dict(facecolor=c.PALETTE[2], alpha=0.5, edgecolor='None', pad=5.0)
    )

    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.1)


def parseMailArchive():
    months = []
    msgCount = []

    print('Start parsing')

    for fpath in glob.glob(DATASET_DIR + '/*.txt'):
        filename = os.path.splitext(os.path.basename(fpath))[0];
        fileDate = datetime.strptime(filename, '%Y-%B')
        if (fileDate.year >= 2012):
            months.append(fileDate)
            msgCount.append(countLines(fpath))

    print('Parsing finished')

    return pd.DataFrame({'MONTH': months,'MSG_COUNT': msgCount}).sort_values(by=['MONTH'])


def countLines(fpath):
    count = 0
    with open(fpath) as file:
        for line in file:
            if line.startswith('Message-ID:'):
                count += 1
    return count
