import time


def busy_sleep(seconds):
    max_time = time.time() + int(seconds)
    while time.time() < max_time:
        pass

def swallow_exception():
    try:
        while True:
            pass
    except:
        pass
