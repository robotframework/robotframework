import logging
from robot.api import logger


ROBOT_LISTENER_API_VERSION = 2


def get_logging_listener_method(name):
    def listener_method(*args):
        if name in ['message', 'log_message']:
            msg = args[0]
            message = '%s: %s %s' % (name, msg['level'], msg['message'])
        else:
            message = name
        logging.info(message)
        logger.warn(message)
    return listener_method


for name in ['start_suite', 'end_suite', 'start_test', 'end_test',
             'start_keyword', 'end_keyword', 'log_message', 'message',
             'output_file', 'log_file', 'report_file', 'debug_file', 'close']:
    globals()[name] = get_logging_listener_method(name)
