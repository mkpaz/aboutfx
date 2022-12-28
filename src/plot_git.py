import glob
import csv
import os
import json
from datetime import datetime

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

import src.constants as c

DATASET_DIR = './dataset/git/uncompressed'

GIT_LOG_COLS = ['HASH', 'AUTHOR', 'AUTHOR_DATE']
CLOC_COLS = [
    'HASH', 'TAG_DATE', 'TAG',
    'N_FILES', 'N_BLANK', 'N_COMMENT', 'N_CODE',
    'N_CODE_JAVA', 'N_FILES_JAVA',
    'N_CODE_C',    'N_FILES_C',
    'N_CODE_HDR',  'N_FILES_HDR',
    'N_CODE_CPP',  'N_FILES_CPP'
]


def start():
    # plotGitLog()
    plotCloc()

###############################################################################
# Git Log                                                                     #
###############################################################################


def plotGitLog():
    df = extractGitLog()

    df['YEAR_COMMITTED'] = df['AUTHOR_DATE'].dropna().apply(lambda x: '%d' %
                                                            (x.year))
    commitsByYear = df['YEAR_COMMITTED'].value_counts().sort_index()
    commitsByAuthor = df.groupby(['YEAR_COMMITTED'])['AUTHOR'].nunique()

    commitCount = df['HASH'].size
    authorCount = df['AUTHOR'].nunique()
    indices = np.arange(commitsByYear.size)
    centerXPos = indices[(len(indices) // 2)]
    centerYPos = commitsByYear.values.max() // 2
    barWidth = 0.3

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.figure(figsize=(10, 6), dpi=80)
    plt.xticks(indices + barWidth / 2, commitsByYear.index.tolist())

    bar1 = plt.bar(indices, commitsByYear.tolist(), barWidth, label='Commits')
    bar2 = plt.bar(indices + barWidth, commitsByAuthor.tolist(),
                   barWidth, label='Authors')

    for rect in bar1 + bar2:
        height = rect.get_height()
        plt.text(
            rect.get_x() + rect.get_width() / 2.0, height + 5, f'{height:.0f}',
            alpha=0.8, ha='center', va='bottom'
        )

    plt.text(
        centerXPos, centerYPos, '{:<5} commits\n{:<5} unique committers'.format(commitCount, authorCount), fontsize=12, ha='left', va='center',
        bbox=dict(facecolor=c.PALETTE[2], alpha=0.5, edgecolor='None', pad=5.0)
    )

    plt.title('Author and Commit Count', pad=16)
    plt.legend(loc='best')
    plt.savefig(c.CHARTS_DIR + '/git_authors-plus-commits.png',
                dpi=100, bbox_inches='tight', pad_inches=0.3)

    mpl.rcParams.update(mpl.rcParamsDefault)


def extractGitLog():
    dateCols = ['AUTHOR_DATE']

    if (os.path.exists(DATASET_DIR + '/git-log.pd.csv')):
        return pd.read_csv(DATASET_DIR + '/git-log.pd.csv', quoting=csv.QUOTE_ALL, parse_dates=dateCols)

    print('Start parsing')

    dataset = []
    with open(DATASET_DIR + '/git-log.json') as file:
        for commit in json.load(file):
            dataset.append({
                'HASH': commit['commitHash'],
                'AUTHOR': commit['author']['name'],
                'AUTHOR_DATE': datetime.fromisoformat(commit['author']['dateISO8601'])
            })

    df = pd.DataFrame(dataset, columns=GIT_LOG_COLS)
    df.to_csv(DATASET_DIR + '/git-log.pd.csv', quoting=csv.QUOTE_ALL)

    print('Parsing finished')

    return df

###############################################################################
# CLOC                                                                        #
###############################################################################

def plotCloc():
    df = extractCloc().sort_values(by='TAG_DATE')
    df['N_CODE_C_SUM'] = df['N_CODE_CPP'] + df['N_CODE_C'] + df['N_CODE_HDR']
    df['N_FILES_C_SUM'] = df['N_FILES_CPP'] + df['N_FILES_C'] + df['N_FILES_HDR']

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    dates = df['TAG_DATE'].tolist()

    ##### Lines of Codes #####

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(500_000))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / 1_000_000)))
    ax.set_ylabel('Count (in millions)')

    plt.rc('axes', axisbelow=True)
    plt.grid()

    ax.plot(dates, df['N_CODE'], label='Any Code', linewidth=2)
    ax.plot(dates, df['N_CODE_JAVA'], label='Java', linewidth=2)
    ax.plot(dates, df['N_CODE_C_SUM'], label='C/C++ (w/ headers)', linewidth=2)
    ax.plot(dates, df['N_COMMENT'], label='Comments', linewidth=2)
    ax.plot(dates, df['N_BLANK'], label='Blank Lines', linewidth=2)

    plt.title('Lines of Code', pad=16)
    plt.legend(loc='best')
    plt.savefig(c.CHARTS_DIR + '/git_lines-of-code.png',
                dpi=100, bbox_inches='tight', pad_inches=0.3)

    ##### Files #####

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.rc('axes', axisbelow=True)
    plt.grid()

    ax.plot(dates, df['N_FILES'], label='Total', linewidth=2)
    ax.plot(dates, df['N_FILES_JAVA'], label='Java', linewidth=2)
    ax.plot(dates, df['N_FILES_C_SUM'], label='C/C++ (w/ headers)', linewidth=2)

    plt.title('File Count', pad=16)
    plt.legend(loc='best')
    plt.savefig(c.CHARTS_DIR + '/git_file-count.png',
                dpi=100, bbox_inches='tight', pad_inches=0.3)

    mpl.rcParams.update(mpl.rcParamsDefault)
    plt.show()


def extractCloc():
    dateCols = ['TAG_DATE']

    if (os.path.exists(DATASET_DIR + '/cloc.pd.csv')):
        return pd.read_csv(DATASET_DIR + '/cloc.pd.csv', quoting=csv.QUOTE_ALL, parse_dates=dateCols)

    print('Start parsing')

    dataset = []
    for fpath in glob.glob(DATASET_DIR + '/cloc_*.json'):
        with open(fpath) as file:
            for entry in json.load(file):
                row = {
                    'HASH': entry['hash'],
                    'TAG_DATE': datetime.strptime(entry['date'], '%Y-%m-%d'),
                    'TAG': entry['tag'],
                    'N_FILES': entry['cloc']['SUM']['nFiles'],
                    'N_BLANK': entry['cloc']['SUM']['blank'],
                    'N_COMMENT': entry['cloc']['SUM']['comment'],
                    'N_CODE': entry['cloc']['SUM']['code']
                }

                if 'Java' in entry['cloc']:
                    row['N_CODE_JAVA'] = entry['cloc']['Java']['code']
                    row['N_FILES_JAVA'] = entry['cloc']['Java']['nFiles']
                else:
                    row['N_CODE_JAVA'] = 0
                    row['N_FILES_JAVA'] = 0

                if 'C' in entry['cloc']:
                    row['N_CODE_C'] = entry['cloc']['C']['code']
                    row['N_FILES_C'] = entry['cloc']['C']['nFiles']
                else:
                    row['N_CODE_C'] = 0
                    row['N_FILES_C'] = 0

                if 'C/C++ Header' in entry['cloc']:
                    row['N_CODE_HDR'] = entry['cloc']['C/C++ Header']['code']
                    row['N_FILES_HDR'] = entry['cloc']['C/C++ Header']['nFiles']
                else:
                    row['N_CODE_HDR'] = 0
                    row['N_FILES_HDR'] = 0

                if 'C++' in entry['cloc']:
                    row['N_CODE_CPP'] = entry['cloc']['C++']['code']
                    row['N_FILES_CPP'] = entry['cloc']['C++']['nFiles']
                else:
                    row['N_CODE_CPP'] = 0
                    row['N_FILES_CPP'] = 0

                dataset.append(row)

    df = pd.DataFrame(dataset, columns=CLOC_COLS)
    df.to_csv(DATASET_DIR + '/cloc.pd.csv', quoting=csv.QUOTE_ALL)

    print('Parsing finished')

    return df


def parseGitDate(date):
    return
