import time

class Library:
    def busy_sleep(self, seconds):
        max_time = time.time() + int(seconds)
        while time.time() < max_time:
            pass
