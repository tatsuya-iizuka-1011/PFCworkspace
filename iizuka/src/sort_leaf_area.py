import datetime
import pandas as pd


CSV_PATH = '/home/iizuka/foodcomputer-vm/output/csv'
file_name = 'contour_area.csv'
df = pd.read_csv('{}/{}'.format(CSV_PATH, file_name))


def to_datetime(filename):
    unixTime = int(filename.split('.')[0])
    return datetime.datetime.fromtimestamp(unixTime)


df.rename(columns={'Unnamed: 0': 'timestamp'}, inplace=True)
df.timestamp = df.timestamp.apply(to_datetime)

df.sort_values(
        by='timestamp', ascending=True
    ).to_csv(
        '{}/contour_area_sorted.csv'.format(CSV_PATH)
    )
