import sys
from robot.output import LOGGER, Message


def write(msg, level, html=False):
    LOGGER.log_message(Message(msg, level, html))

def trace(msg, html=False):
    write(msg, 'TRACE', html)

def debug(msg, html=False):
    write(msg, 'DEBUG', html)

def info(msg, html=False, also_console=False):
    write(msg, 'INFO', html)
    if also_console:
        console(msg)

def warn(msg, html=False):
    write(msg, 'WARN', html)

def console(msg, newline=True):
    if newline:
        msg += '\n'
    sys.__stdout__.write(msg)
