import sys
from robot.libraries.BuiltIn import BuiltIn
from collections import OrderedDict

class global_vars_listenerlibrary():
    ROBOT_LISTENER_API_VERSION = 2

    global_vars = OrderedDict([("Suite name:", "${SUITE_NAME}"),
                               ("Suite documentation:", "${SUITE_DOCUMENTATION}"),
                               ("Previous test name:", "${PREV_TEST_NAME}"),
                               ("Previous test status:", "${PREV_TEST_STATUS}"),
                               ("Log level:", "${LOG_LEVEL}")])

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self

    def _close(self):
        for var, value in self.global_vars.items():
            sys.__stderr__.write(var + (BuiltIn().get_variable_value(value)) +"\n")
