import matplotlib as mpl
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

import src.constants as c

DATASET_DIR = './dataset/mail/uncompressed'

def start():
    plotReleasesTimeline(c.CHARTS_DIR + '/releases.png')
    mpl.rcParams.update(mpl.rcParamsDefault)

    plt.show()


def plotReleasesTimeline(fpath):
    names = c.RELEASES.keys()
    dates = list(c.RELEASES.values())
    levels = np.tile([-5, 5, -3, 3, -1, 1], int(np.ceil(len(dates)/6)))[:len(dates)]
    vLineColor = c.PALETTE[3]

    sns.set_palette(c.PALETTE)
    plt.rcParams['font.family'] = 'monospace'
    plt.rc('axes', axisbelow=True)

    fig, ax = plt.subplots(figsize=(8.8, 4), constrained_layout=True)
    ax.set(title="JavaFX Release Dates")

    ax.vlines(dates, 0, levels, color=vLineColor)
    ax.plot(dates, np.zeros_like(dates), "-o", color="k", markerfacecolor="w")  # Baseline and markers on it.
    ax.grid()

    # annotate lines
    for date, level, name in zip(dates, levels, names):
        ax.annotate("v" + name, xy=(date, level), xytext=(-3, np.sign(level) * 3), textcoords="offset points",
                    ha="left", va="bottom" if level > 0 else "top"
        )

    # format xaxis with 4 month intervals
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # remove y axis and spines
    ax.yaxis.set_visible(False)
    ax.spines[["left", "top", "right"]].set_visible(False)

    ax.margins(y=0.1)

    plt.savefig(fpath, dpi=100, bbox_inches='tight', pad_inches=0.1)
