from time import time, sleep


class FailUntilSucceeds:
    ROBOT_LIBRARY_SCOPE = 'TESTCASE'

    def __init__(self, times_to_fail=0):
        self.times_to_fail = int(times_to_fail)
        self.last_call_time = None

    def set_times_to_fail(self, times_to_fail):
        self.__init__(times_to_fail)

    def fail_until_retried_often_enough(self, message="Hello"):
        self.times_to_fail -= 1
        if self.times_to_fail >= 0:
            raise Exception('Still %d times to fail!' % self.times_to_fail)
        return message

    def passes_every_second_time_at_50ms_interval(self, message="Hello"):
        if not self.last_call_time:
            self.last_call_time = time()
        elapsed = time() - self.last_call_time
        if elapsed % 0.05 > 0.01 or elapsed < 0.045:
            sleep(0.02)  # insert 20ms delay to interfere with the timing
            raise TimeoutError('interval violated')
        self.last_call_time = None  # Resetting call time
        return message
