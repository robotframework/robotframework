import logging
import time
import sys


class CustomHandler(logging.Handler):

    def emit(self, record):
        sys.__stdout__.write(record.getMessage().title() + '\n')

custom = logging.getLogger('custom')
custom.addHandler(CustomHandler())
nonprop = logging.getLogger('nonprop')
nonprop.propagate = False
nonprop.addHandler(CustomHandler())


class Message(object):
    def __init__(self, msg=''):
        self.msg = msg
    def __unicode__(self):
        return self.msg
    def __str__(self):
        return unicode(self).encode('UTF-8')
    def __repr__(self):
        return repr(str(self))

class InvalidMessage(Message):
    def __unicode__(self):
        raise AssertionError('Should not have been logged')


def log_with_default_levels():
    logging.debug('debug message')
    logging.info('%s %s', 'info', 'message')
    logging.warning(Message('warning message'))
    # error and critical are considered warnings
    logging.error('error message')
    logging.critical('critical message')

def log_with_custom_levels():
    logging.log(logging.DEBUG-1, Message('below debug'))
    logging.log(logging.INFO-1, 'between debug and info')
    logging.log(logging.INFO+1, 'between info and warning')
    logging.log(logging.WARNING*100, 'above warning')

def log_invalid_message_using_debug():
    logging.debug(InvalidMessage())

def log_using_custom_logger():
    logging.getLogger('custom').info('custom logger')

def log_using_non_propagating_logger():
    logging.getLogger('nonprop').info('nonprop logger')

def log_messages_different_time():
    logging.info('First message')
    time.sleep(0.1)
    logging.info('Second message 0.1 sec later')
