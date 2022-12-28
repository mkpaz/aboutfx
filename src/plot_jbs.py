import csv
import glob
import math
import os
import xml.etree.ElementTree as et
from datetime import datetime
from email.utils import mktime_tz, parsedate_tz

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pywaffle import Waffle

import src.constants as c

DATASET_DIR = './dataset/jbs/uncompressed'
JBS_COLS = [
    "KEY", "TITLE", "TYPE", "STATUS", "CREATED", "RESOLVED", "RESOLUTION", "FIX_VERSION", "COMPONENT"
]

def start():
    df = extractDataset()

    plotIssuesByComponent(df, c.CHARTS_DIR + '/jbs_issues-by-component.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotResolvedByVersion(df, c.CHARTS_DIR + '/jbs_fixed-issues-by-version.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotOpenIssuesAge(df, c.CHARTS_DIR + '/jbs_open-issues-age.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotCreatedVsResolved(df, c.CHARTS_DIR + '/jbs_created-vs-resolved.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotAllIssuesByType(df, c.CHARTS_DIR + '/jbs_all-issues-by-type.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotOpenIssuesByType(df, c.CHARTS_DIR + '/jbs_open-issues-by-type.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotAllIssuesByStatus(df, c.CHARTS_DIR + '/jbs_all-issues-by-status.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotResolvedIssuesByReason(df, c.CHARTS_DIR + '/jbs_resolved-issues-by-reason.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plotYearCharts(df)

    #plt.show()


def plotYearCharts(df):
    df['YEAR_RESOLVED'] = df['RESOLVED'].dropna().apply(lambda x: '%d' % (x.year))
    resolved = df.query('STATUS in ("Resolved", "Closed") & YEAR_RESOLVED == @c.YEAR')

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    data = resolved['RESOLUTION'].value_counts().to_dict()
    plt.figure(
        FigureClass=Waffle, rows=5, columns=20, values=data, block_arranging_style='snake',
        title={'label': 'Issues Resolved in 2022 by Reason', 'pad': 16},
        legend={
            'labels': [f"{v:<3} {k}" for k, v in data.items()],
            'loc': 'lower left',
            'bbox_to_anchor': (0, -0.85),
            'ncol': 2,
            'framealpha': 0,
            'fontsize': 10
        }
    )
    plt.savefig('{}/jbs_{}_by-status.png'.format(c.CHARTS_DIR, c.YEAR), dpi=100, bbox_inches='tight', pad_inches=0.1)

    data = resolved['COMPONENT'].value_counts().to_dict()
    plt.figure(
        FigureClass=Waffle, rows=5, columns=20, values=data, block_arranging_style='snake',
        title={'label': 'Issues Resolved in 2022 by Component', 'pad': 16},
        legend={
            'labels': [f"{v:<3} {k}" for k, v in data.items()],
            'loc': 'lower left',
            'bbox_to_anchor': (0, -1.1),
            'ncol': 2,
            'framealpha': 0,
            'fontsize': 10
        }
    )
    plt.savefig('{}/jbs_{}_by-component.png'.format(c.CHARTS_DIR, c.YEAR), dpi=100, bbox_inches='tight', pad_inches=0.1)

    data = resolved['TYPE'].value_counts().to_dict()
    plt.figure(
        FigureClass=Waffle, rows=5, columns=20, values=data, block_arranging_style='snake',
        title={'label': 'Issues Resolved in 2022 by Type', 'pad': 16},
        legend={
            'labels': [f"{v:<3} {k}" for k, v in data.items()],
            'loc': 'lower left',
            'bbox_to_anchor': (0, -0.5),
            'ncol': 3,
            'framealpha': 0,
            'fontsize': 10
        }
    )
    plt.savefig('{}/jbs_{}_by-type.png'.format(c.CHARTS_DIR, c.YEAR), dpi=100, bbox_inches='tight', pad_inches=0.1)

    mpl.rcParams.update(mpl.rcParamsDefault)

def plotIssuesByComponent(df, fpath):
    all = df['COMPONENT'].value_counts()
    open = df.query('STATUS in ("Open", "New")')['COMPONENT'].value_counts()

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    plt.rc('axes', axisbelow=True) # move grid to the background
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
    plt.gcf().subplots_adjust(bottom=0.3)

    ax1.bar(all.index.tolist(), all.tolist())
    ax1.set_title('All Issues by Component', pad=16)
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(500))
    ax1.grid()
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8, fontfamily='sans-serif')

    ax2.bar(open.index.tolist(), open.tolist())
    ax2.set_title('Open Issues by Component', pad=16)
    ax2.yaxis.set_major_locator(ticker.MultipleLocator(100))
    ax2.grid()
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8, fontfamily='sans-serif')

    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.1)


def plotResolvedByVersion(df, fpath):
    stats = df.query('RESOLUTION == "Fixed"')['FIX_VERSION'].value_counts();
    stats = stats.reindex(index=stats.index.to_series().str[1:].astype(int).sort_values().index)

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.bottom'] = False
    plt.rcParams['axes.spines.left'] = False

    fig, ax = plt.subplots(figsize=(10, 8))
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=True)

    ax.barh(stats.index, stats.tolist())

    for rect in ax.patches:
        width = rect.get_width()
        plt.text(width + 50, rect.get_y() + rect.get_height() / 2, f'{width:.0f}', alpha=0.8, ha='left', va='center')

    plt.title('Fixed Issues by Version')

    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.1)


def plotOpenIssuesAge(df, fpath):
    df['YEAR_CREATED'] = df['CREATED'].dropna().apply(lambda x: '%d' % (x.year))
    bugs = df.query('STATUS in ("Open", "New") and TYPE == "Bug"')['YEAR_CREATED'].value_counts().sort_index()
    features = df.query('STATUS in ("Open", "New") and TYPE == "Enhancement"')['YEAR_CREATED'].value_counts().sort_index()

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.bottom'] = False
    plt.rcParams['axes.spines.left'] = False

    fig, ax = plt.subplots(figsize=(10, 8))
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=True)
    ax.yaxis.set_major_locator(mdates.YearLocator(1))
    ax.yaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # fix y axis scaling, otherwise it shows dates that is no in dataset
    barHeight = 250
    plt.ylim(
        pd.to_datetime(bugs.index.min()) - pd.DateOffset(barHeight),
        pd.to_datetime(bugs.index.max()) + pd.DateOffset(barHeight)
    )

    b1 = ax.barh(pd.to_datetime(bugs.index, format='%Y'), bugs.tolist(), height=barHeight)
    b2 = ax.barh(pd.to_datetime(bugs.index, format='%Y'), features.tolist(), left=bugs.tolist(), height=barHeight)

    patches = []
    for r in b1.patches:
        patches.append({'v1' : r.get_width(), 'height' : r.get_y() + r.get_height() / 2})
    for idx, r in enumerate(b2.patches):
        patches[idx]['v2'] = r.get_width()
    for p in patches:
        width = p['v1'] + p['v2'] + 10
        plt.text(width, p['height'], '{}/{}'.format(p['v1'], p['v2']), alpha=0.8, ha='left', va='center')

    plt.xlabel('Issue Count')
    plt.ylabel('Issue Created at')
    plt.legend([b1, b2], ['Bug', 'Enhancement'])
    plt.title('Open Issues Age')

    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.1)


def plotCreatedVsResolved(df, fpath):
    df['YEAR_CREATED'] = df['CREATED'].dropna().apply(lambda x: '%d' % (x.year))
    created = df['YEAR_CREATED'].value_counts().sort_index()

    df['YEAR_RESOLVED'] = df['RESOLVED'].dropna().apply(lambda x: '%d' % (x.year))
    resolved = df['YEAR_RESOLVED'].value_counts().sort_index()

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    indices = np.arange(created.size)
    barWidth = 0.3
    plt.figure(figsize=(10, 5))

    plt.rc('axes', axisbelow=True) # move grid to the background
    plt.grid()

    plt.bar(indices, created.tolist(), barWidth, label='Created')
    plt.bar(indices + barWidth, resolved.tolist(), barWidth, label='Resolved')
    plt.xticks(indices + barWidth / 2, resolved.index.tolist())
    plt.legend(loc='best')
    plt.ylabel('Issue Count')

    plt.title('Created vs Resolved Issues', pad=16)

    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.1)


def plotAllIssuesByType(df, fpath):
    plotVerticalBarChart(
        df['TYPE'].value_counts(), 'All Issues by Type', fpath
    )


def plotOpenIssuesByType(df, fpath):
    plotVerticalBarChart(
        df.query('STATUS in ("Open", "New")')['TYPE'].value_counts(), 'Open Issues by Type', fpath
    )


def plotAllIssuesByStatus(df, fpath):
    plotVerticalBarChart(
        df['STATUS'].value_counts(), 'All Issues by Status', fpath
    )


def plotResolvedIssuesByReason(df, fpath):
    plotVerticalBarChart(
        df.query('STATUS in ("Resolved", "Closed")')['RESOLUTION'].value_counts(), 'Resolved Issues by Reason', fpath
    )


def plotVerticalBarChart(df, title, fpath):
    index = df.index.tolist()
    data = df.tolist()
    total = df.sum()

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'

    # Important note: mathplotlib doesn't provide such type of a chart out-of-the-box,
    # so there's quite a lot of work here. All sizes, paddings and coordinates are
    # selected empirically for the better visualization.
    ax = df.to_frame().T.plot.bar(stacked=True, legend=True, figsize=(6, 6))

    plt.title(title, loc='left')
    plt.xlim(0, -1)         # remove plot paddings
    plt.margins(None, None) # ... and also margins
    plt.axis('off')

    # add item value to the legend
    plt.legend(loc='upper left', bbox_to_anchor=(0.3, 0.85),
        labels=['{:6} {}'.format(str(val), lbl) for lbl, val in zip(index, data)], prop={'family': 'monospace'}
    )

    # add percentage label to the bar
    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        x, y = p.get_xy()
        ax.text(x / 2, y + height / 2, getPercentageLabel(height, total), ha='center', va='center')

    # add total label above the legend
    plt.text(
        -0.33, total * 0.95, 'Total = {}'.format(total), fontsize=12, ha='left', va='center',
        bbox=dict(facecolor=c.PALETTE[2], alpha=0.5, edgecolor='None', pad=5.0)
    )

    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.1)


def getPercentageLabel(val, total):
    p = (100 / total) * val
    if p > 5:  # ax.patch height must be greater than text font size, selected empirically
        return '{}%'.format(math.ceil(p))
    else:
        return ''


###############################################################################
# PARSE                                                                       #
###############################################################################

def extractDataset():
    # cache search result because parsing 350MB of XML is expensive
    dateCols = ['CREATED', 'RESOLVED']

    if (os.path.exists(DATASET_DIR + '/jbs.pd.csv')):
        return pd.read_csv(DATASET_DIR + '/jbs.pd.csv', quoting=csv.QUOTE_ALL, parse_dates=dateCols)

    print('Start parsing')

    rows = []
    for fpath in glob.glob(DATASET_DIR + '/SearchRequest*.xml'):
        rows.extend(parseXml(fpath))

    df = pd.DataFrame(rows, columns=JBS_COLS);
    df.to_csv(DATASET_DIR + '/jbs.pd.csv', quoting=csv.QUOTE_ALL)

    print('Parsing finished')

    return df


def parseXml(fpath):
    rows = []

    xml = et.parse(fpath)
    items = xml.findall('.//channel/item')

    for item in items:
        row = {}
        row['KEY']     = item.find('key').text
        row['TITLE']   = item.find('title').text
        row['TYPE']    = item.find('type').text
        row['STATUS']  = item.find('status').text
        row['CREATED'] = parseJBSDate(item.find('created').text)

        resolved = item.find('resolved')
        if resolved != None:
            row['RESOLVED'] = parseJBSDate(resolved.text)

        resolution = item.find('resolution')
        if resolution != None:
            row['RESOLUTION'] = resolution.text

        # this extracts major version from the version string which has no common format in the database
        # pseudo regex: (noise)?(major version digits)(non-digit separator)(minor version w/ or w/o separators)(noise)?
        fixVersion = item.find('fixVersion')
        if fixVersion != None:
            majorVersion = []
            for c in fixVersion.text:
                if c.isdigit():
                    majorVersion.append(c)
                else:
                    if len(majorVersion) > 0:
                        break
                    else:
                        continue

            if len(majorVersion) > 0:
                row['FIX_VERSION'] = 'v' + ''.join(majorVersion)

        subComponents = item.findall('./customfields/customfield[@key="com.oracle.jira.jira-subcomponent-plugin:oracle-subComponentField"]/customfieldvalues/customfieldvalue')
        if subComponents != None:
            values = []
            for c in subComponents:
                values.append(c.text)
            row['COMPONENT'] = '&'.join(values)

        rows.append(row)

    return rows


def parseJBSDate(date):
    return datetime.fromtimestamp(mktime_tz(parsedate_tz(date)))
