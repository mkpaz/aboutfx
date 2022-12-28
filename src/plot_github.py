import csv
import json
import math
import os
from datetime import datetime

import matplotlib as mpl
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import src.constants as c

DATASET_DIR = './dataset/github/uncompressed'
PR_COLS = ['NUMBER', 'STATE', 'TITLE', 'USERNAME', 'CREATED_AT', 'CLOSED_AT']
STAR_COLS = ['USERNAME', 'STARRED_AT']

def start():

    plotReposByDate(c.CHARTS_DIR + '/github_created-repos-by-date.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotPullRequestsByDate(c.CHARTS_DIR + '/github_pr-by-date.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotStarsByDate(c.CHARTS_DIR + '/github_stars-by-date.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    #plt.show()

def parseGithubDate(date):
    if date is not None:
        return datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    else:
        return None


###############################################################################
# Repositories                                                                #
###############################################################################

def plotReposByDate(fpath):
    dataset = []
    with open(DATASET_DIR + '/repo-stats.json') as file:
        for entry in json.load(file):
            dataset.append({
                'DATE': datetime.strptime(entry['date'], '%Y-%m'),
                'COUNT': entry['count']
            })

    df = pd.DataFrame(dataset, columns=['DATE', 'COUNT'])
    meanPerYear = df.groupby(df.DATE.dt.year)['COUNT'].agg(['mean'])
    meanPerMonth = math.ceil(df[df['DATE'] > "2017-01-01"]['COUNT'].agg(['mean']))

    sns.set_palette(c.PALETTE)
    barColor = c.PALETTE[2]
    plt.rcParams['font.family'] = 'monospace'
    plt.rc('axes', axisbelow=True)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(True, axis='both')

    plt.ylabel('Repo Count')
    plt.title('Number of Created Github Repos (marked with @javafx)', pad=16)

    # two charts on a single plot
    line = sns.lineplot(x=df['DATE'], y=df['COUNT'], ax=ax)
    ax.bar(pd.to_datetime(
        meanPerYear.index, format='%Y'), meanPerYear['mean'],
        width=365, alpha=0.5, color=barColor, align='edge'
    )

    line.set(xlabel=None)
    plt.xlabel(None)

    plt.text(
        df['DATE'].min(), meanPerMonth, '{} new repos per month\n    since 2017'.format(meanPerMonth), fontsize=12, ha='left', va='center',
        bbox=dict(facecolor=c.PALETTE[2], alpha=0.5, edgecolor='None', pad=5.0)
    )

    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.3)


def loadStarsDataset():
    dateCols = ['STARRED_AT']

    if (os.path.exists(DATASET_DIR + '/stars.pd.csv')):
        return pd.read_csv(DATASET_DIR + '/stars.pd.csv', quoting=csv.QUOTE_ALL, parse_dates=dateCols)

    print('Start Parsing')

    dataset = []
    with open(DATASET_DIR + '/stars.json') as file:
        jsonData = json.load(file)
        for page in jsonData:
            for entry in page:
                dataset.append({
                    'USERNAME': entry['user']['login'],
                    'STARRED_AT': parseGithubDate(entry['starred_at'])
                })

    df = pd.DataFrame(dataset, columns=STAR_COLS)
    df.to_csv(DATASET_DIR + '/stars.pd.csv', quoting=csv.QUOTE_ALL)

    print('Parsing finished')

    return df

###############################################################################
# Pull Requests                                                               #
###############################################################################

def plotPullRequestsByDate(fpath):
    df = loadPullRequestsDataset()

    df['YEAR_CREATED'] = df['CREATED_AT'].dropna().apply(lambda x: '%d' % (x.year))
    createdStats = df['YEAR_CREATED'].value_counts().sort_index()

    df['YEAR_CLOSED'] = df['CLOSED_AT'].dropna().apply(lambda x: '%d' % (x.year))
    closedStats = df['YEAR_CLOSED'].value_counts().sort_index()

    openCount = df.query('STATE == "open"')['STATE'].count()
    closedCount = df.query('STATE == "closed"')['STATE'].count()
    centerYPos = math.ceil((createdStats.mean() + closedStats.mean()) / 2)
    indices = np.arange(createdStats.size)
    barWidth = 0.3

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.figure(figsize=(10, 6), dpi=80)
    plt.xticks(indices + barWidth / 2, createdStats.index.tolist())
    plt.ylabel('PR')

    bar1 = plt.bar(indices, createdStats.tolist(), barWidth, label='Created')
    bar2 = plt.bar(indices + barWidth, closedStats.tolist(), barWidth, label='Closed')

    for rect in bar1 + bar2:
        height = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0, height + 5, f'{height:.0f}',
            alpha=0.8 , ha='center', va='bottom'
        )

    plt.text(
        indices[0], centerYPos, 'Open   = {}\nClosed = {}'.format(openCount, closedCount), fontsize=12, ha='left', va='center',
        bbox=dict(facecolor=c.PALETTE[2], alpha=0.5, edgecolor='None', pad=5.0)
    )

    plt.title('Created vs Closed Pull Requests', pad=16)
    plt.legend(loc='best')
    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.3)


def loadPullRequestsDataset():
    dateCols = ['CREATED_AT', 'CLOSED_AT']

    if (os.path.exists(DATASET_DIR + '/pull-requests.pd.csv')):
        return pd.read_csv(DATASET_DIR + '/pull-requests.pd.csv', quoting=csv.QUOTE_ALL, parse_dates=dateCols)

    print('Start parsing')

    dataset = []
    with open(DATASET_DIR + '/pull-requests.json') as file:
        jsonData = json.load(file)
        for page in jsonData:
            for entry in page:
                dataset.append({
                    'NUMBER': entry['number'],
                    'STATE': entry['state'],
                    'TITLE': entry['title'],
                    'USERNAME': entry['user']['login'],
                    'CREATED_AT': parseGithubDate(entry['created_at']),
                    'CLOSED_AT': parseGithubDate(entry['closed_at'])
                })

    df = pd.DataFrame(dataset, columns=PR_COLS)
    df.to_csv(DATASET_DIR + '/pull-requests.pd.csv', quoting=csv.QUOTE_ALL)

    print('Parsing finished')

    return df

###############################################################################
# Stars                                                                       #
###############################################################################

def plotStarsByDate(fpath):
    df = loadStarsDataset()
    df = df.groupby(pd.Grouper(key='STARRED_AT', freq='M')) \
            .agg(COUNT=pd.NamedAgg(column='USERNAME', aggfunc='count')) \
            .reset_index()
    meanCount = math.ceil(df['COUNT'].mean())
    meanDate = df['STARRED_AT'].mean()

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    plt.rc('axes', axisbelow=True)
    plt.figure(figsize=(10, 6), dpi=80)
    plt.grid(True, axis='both')
    plt.ylabel('Stars')
    plt.title('Number of GitHub Stars per Month', pad=16)
    plt.text(
        meanDate, 15, 'Average per Month = {}'.format(meanCount), fontsize=12, ha='center', va='center',
        bbox=dict(facecolor=c.PALETTE[2], alpha=0.5, edgecolor='None', pad=5.0)
    )

    plt.plot(df['STARRED_AT'], df['COUNT'])
    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.3)


def loadStarsDataset():
    dateCols = ['STARRED_AT']

    if (os.path.exists(DATASET_DIR + '/stars.pd.csv')):
        return pd.read_csv(DATASET_DIR + '/stars.pd.csv', quoting=csv.QUOTE_ALL, parse_dates=dateCols)

    print('Start Parsing')

    dataset = []
    with open(DATASET_DIR + '/stars.json') as file:
        jsonData = json.load(file)
        for page in jsonData:
            for entry in page:
                dataset.append({
                    'USERNAME': entry['user']['login'],
                    'STARRED_AT': parseGithubDate(entry['starred_at'])
                })

    df = pd.DataFrame(dataset, columns=STAR_COLS)
    df.to_csv(DATASET_DIR + '/stars.pd.csv', quoting=csv.QUOTE_ALL)

    print('Parsing finished')

    return df
