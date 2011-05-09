from robot.output import LOGGER, Message


def write(msg, level, html=False):
    LOGGER.log_message(Message(msg, level, html))

def trace(msg, html=False):
    write(msg, 'TRACE', html)

def debug(msg, html=False):
    write(msg, 'DEBUG', html)

def info(msg, html=False):
    write(msg, 'INFO', html)

def warn(msg, html=False):
    write(msg, 'WARN', html)

