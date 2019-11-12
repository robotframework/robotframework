import sys

from robot.libraries.BuiltIn import BuiltIn


class global_vars_listenerlibrary():
    ROBOT_LISTENER_API_VERSION = 2

    global_vars = ["${SUITE_NAME}",
                   "${SUITE_DOCUMENTATION}",
                   "${PREV_TEST_NAME}",
                   "${PREV_TEST_STATUS}",
                   "${LOG_LEVEL}"]

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self

    def _close(self):
        for var in self.global_vars:
            sys.__stderr__.write('%s: %s\n' % (var, BuiltIn().get_variable_value(var)))
