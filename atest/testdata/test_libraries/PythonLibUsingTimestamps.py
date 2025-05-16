import time


def timezone_correction():
    dst = 3600 if time.daylight == 0 else 0
    tz = 7200 + time.timezone
    return (tz + dst) * 1000


def timestamp_as_integer():
    known = 1308419034931 + timezone_correction()
    current = int(time.time() * 1000)
    print(f"*INFO:{known}* Known timestamp")
    print(f"*HTML:{current}* <b>Current</b>")
    time.sleep(0.1)


def timestamp_as_float():
    known = 1308419034930.502342313 + timezone_correction()
    current = float(time.time() * 1000)
    print(f"*INFO:{known}* Known timestamp")
    print(f"*HTML:{current}* <b>Current</b>")
    time.sleep(0.1)
