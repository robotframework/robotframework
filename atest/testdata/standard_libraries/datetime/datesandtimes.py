import time
from datetime import date as date, datetime as datetime, timedelta as timedelta

TIMEZONE = time.altzone if time.localtime().tm_isdst else time.timezone
EPOCH = 1542892422.0 + time.timezone  # 2018-11-22 13:13:42
BIG_EPOCH = 6000000000 + time.timezone  # 2160-02-18 10:40:00


def all_days_for_year(year):
    year = int(year)
    dt = datetime(year, 1, 1)
    day = timedelta(days=1)
    while dt.year == year:
        yield dt.strftime("%Y-%m-%d %H:%M:%S")
        dt += day


def year_range(start, end, step=1, format="timestamp"):
    dt = datetime(int(start), 1, 1)
    end = int(end)
    step = int(step)
    while dt.year <= end:
        if format == "datetime":
            yield dt
        elif format == "timestamp":
            yield dt.strftime("%Y-%m-%d %H:%M:%S")
        elif format == "epoch":
            yield dt.timestamp() if dt.year != 1970 else 0
        else:
            raise ValueError(f"Invalid format: {format}")
        dt = dt.replace(year=dt.year + step)
