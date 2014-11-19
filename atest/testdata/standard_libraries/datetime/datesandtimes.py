from datetime import timedelta, datetime
import time

TIMEZONE = time.altzone if time.localtime().tm_isdst else time.timezone
EPOCH = 1398375912.0 + time.altzone
