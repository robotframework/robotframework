from datetime import timedelta, datetime
import time

EPOCH = 1398375912.0 + (time.altzone if time.localtime().tm_isdst else time.timezone)
