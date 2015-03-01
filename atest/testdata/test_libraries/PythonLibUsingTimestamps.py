import time


def timezone_correction():
    dst = 3600 if time.daylight == 0 else 0
    tz = 7200 + time.timezone
    return (tz + dst) * 1000

def timestamp_as_integer():
    t = 1308419034931 + timezone_correction()
    print('*INFO:%d* Known timestamp' % t)
    print('*HTML:%d* <b>Current</b>' % int(time.time() * 1000))
    time.sleep(0.1)

def timestamp_as_float():
    t = 1308419034930.502342313 + timezone_correction()
    print('*INFO:%f* Known timestamp' % t)
    print('*HTML:%f* <b>Current</b>' % float(time.time() * 1000))
    time.sleep(0.1)
