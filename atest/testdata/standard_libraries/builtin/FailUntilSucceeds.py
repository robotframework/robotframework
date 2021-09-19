import time


class FailUntilSucceeds:
    ROBOT_LIBRARY_SCOPE = 'TESTCASE'

    def __init__(self, times_to_fail=0):
        self.times_to_fail = int(times_to_fail)

    def set_times_to_fail(self, times_to_fail):
        self.__init__(times_to_fail)

    def fail_until_retried_often_enough(self, message="Hello", sleep=0):
        self.times_to_fail -= 1
        time.sleep(sleep)
        if self.times_to_fail >= 0:
            raise Exception('Still %d times to fail!' % self.times_to_fail)
        return message
