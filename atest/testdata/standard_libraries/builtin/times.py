import time
import datetime

def get_timestamp_from_date(*args):
    return int(time.mktime(datetime.datetime(*(int(arg) for arg in args)).timetuple()))

def get_current_time_zone():
    return time.altzone if time.localtime().tm_isdst else time.timezone
