import time
from datetime import date, datetime, timedelta


TIMEZONE = time.altzone if time.localtime().tm_isdst else time.timezone
EPOCH = 1542892422.0 + time.timezone      # 2018-11-22 13:13:42
BIG_EPOCH = 6000000000 + time.timezone    # 2160-02-18 10:40:00


def all_days_for_year(year):
    year = int(year)
    dt = datetime(year, 1, 1)
    day = timedelta(days=1)
    while dt.year == year:
        yield dt.strftime('%Y-%m-%d %H:%M:%S')
        dt += day


def year_range(start, end, step=1, format='timestamp'):
    dt = datetime(int(start), 1, 1)
    end = int(end)
    step = int(step)
    while dt.year <= end:
        if format == 'datetime':
            yield dt
        if format == 'timestamp':
            yield dt.strftime('%Y-%m-%d %H:%M:%S')
        if format == 'epocn':
            yield time.mktime(dt.timetuple())
        dt = dt.replace(year=dt.year + step)
