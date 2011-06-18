import time


def timestamp_as_integer():
    print '*INFO:1308419034931* Known timestamp'
    print '*HTML:%d* <b>Current</b>' % int(time.time() * 1000)
    time.sleep(0.1)

def timestamp_as_float():
    print '*INFO:1308419034930.502342313* Known timestamp'
    print '*HTML:%f* <b>Current</b>' % float(time.time() * 1000)
    time.sleep(0.1)
