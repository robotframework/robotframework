import logging
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn


ROBOT_LISTENER_API_VERSION = 2

RECURSION = False


def get_logging_listener_method(name):

    def listener_method(*args):
        global RECURSION
        if RECURSION:
            return
        RECURSION = True
        if name in ['message', 'log_message']:
            msg = args[0]
            message = f"{name}: {msg['level']} {msg['message']}"
        elif name == 'start_keyword':
            message = f"start {args[1]['type']}".lower()
        elif name == 'end_keyword':
            message = f"end {args[1]['type']}".lower()
        else:
            message = name
        logging.info(message)
        logger.warn(message)
        # `set_xxx_variable` methods log normally, but they shouldn't log
        # if they are used by a listener when no keyword is started.
        if name == 'start_suite':
            BuiltIn().set_suite_variable('${SUITE}', 'value')
        if name == 'start_test':
            BuiltIn().set_test_variable('${TEST}', 'value')
        RECURSION = False

    return listener_method


for name in ['start_suite', 'end_suite', 'start_test', 'end_test',
             'start_keyword', 'end_keyword', 'log_message', 'message',
             'output_file', 'log_file', 'report_file', 'debug_file', 'close']:
    globals()[name] = get_logging_listener_method(name)
