
from robot.running.context import EXECUTION_CONTEXTS
from robot.running.timeouts import TotalTimeout

class TimeoutIncreaseListener:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, timeout_string):
        self.timeout_string = timeout_string

    def start_suite(self, data, result):
        try:
             variables = EXECUTION_CONTEXTS.current.variables
        except AttributeError:
             variables = None 
        
        old_timeout = EXECUTION_CONTEXTS.total_timeout
        print(f"DEBUG: Timeout before: {old_timeout}")
        
        # parse new timeout values using a temporary object
        new_timeout_obj = TotalTimeout(self.timeout_string, variables)
        
        # time_left() relies on self.timeout and start_time
        # update self.timeout (duration)
        if new_timeout_obj.timeout is not None:
            old_timeout.timeout = new_timeout_obj.timeout
            old_timeout.string = new_timeout_obj.string
            # this way do NOT reset start_time, so it counts from original start.
                 
        print(f"DEBUG: Timeout after: {EXECUTION_CONTEXTS.total_timeout}")
