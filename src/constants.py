from datetime import datetime

import seaborn as sns

CHARTS_DIR = "./charts"

PALETTE = sns.color_palette('pastel')

RELEASES = {
    '19': datetime(2022, 9, 12),  # 12-Sep-2022
    '18': datetime(2022, 3, 8),  # 08-Mar-2022
    '17': datetime(2021, 9, 7),  # 07-Sep-2021
    '16': datetime(2021, 3, 8),  # 08-Mar-2021
    '15': datetime(2020, 9, 4),  # 04-Sep-2020
    '14': datetime(2020, 3, 10),  # 10-Mar-2020
    '13': datetime(2019, 9, 3),  # 03-Sep-2019
    '12': datetime(2019, 3, 11),  # 11-Mar-2019
    '11': datetime(2018, 9, 13),  # 13-Sep-2018
    '10': datetime(2018, 3, 20),  # 20-Mar-2018, JDK10
    '9':  datetime(2017, 9, 21),  # 21-Sep-2017, JDK9
    '8':  datetime(2014, 3, 18)  # 18-Mar-2014, JDK8
}

YEAR = '2022'
