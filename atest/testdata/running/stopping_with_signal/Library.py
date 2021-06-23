import time


def busy_sleep(seconds):
    max_time = time.time() + int(seconds)
    while time.time() < max_time:
        time.sleep(0)


def swallow_exception(timeout=3):
    try:
        busy_sleep(timeout)
    except:
        pass
    else:
        raise AssertionError('Expected exception did not occur!')
