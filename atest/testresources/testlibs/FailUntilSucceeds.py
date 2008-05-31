import time

class FailUntilSucceeds:
    
    ROBOT_LIBRARY_SCOPE = 'TESTCASE'
    
    def __init__(self, execution_time=None, times_to_fail=None):
        self.execution_time = execution_time
        self.times_to_fail = times_to_fail
    
    def set_execution_time_and_fail_count(self, execution_time, times_to_fail):
        self.execution_time = float(execution_time)
        self.times_to_fail = float(times_to_fail)

    def fail_until_retried_often_enough(self, message="Hello"):
        time.sleep(self.execution_time)
        if self.times_to_fail > 0:
            self.times_to_fail -= 1
            raise Exception('Still %d times to fail!' % (self.times_to_fail))
        else:
            return message