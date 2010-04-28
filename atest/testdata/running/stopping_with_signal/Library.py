import time

class Library:
    def my_sleep(self, seconds):
        start_time = time.time()
        while (time.time() - int(seconds) < start_time):
            time.sleep(1)
