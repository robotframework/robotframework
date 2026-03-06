
from robot.running.context import EXECUTION_CONTEXTS
from robot.running.timeouts import TotalTimeout

class TimeoutListener:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, timeout_string):
        self.timeout_string = timeout_string

    def start_suite(self, data, result):
        try:
             variables = EXECUTION_CONTEXTS.current.variables
        except AttributeError:
             variables = None 
        
        timeout = TotalTimeout(self.timeout_string, variables)
        timeout.start()
        
        # inject it into EXECUTION_CONTEXTS
        EXECUTION_CONTEXTS.total_timeout = timeout
