import time


def busy_sleep(seconds):
    max_time = time.time() + int(seconds)
    while time.time() < max_time:
        pass

def swallow_exception(timeout=3):
    try:
        busy_sleep(timeout)
    except:
        pass
    else:
        raise AssertionError('No exception')
