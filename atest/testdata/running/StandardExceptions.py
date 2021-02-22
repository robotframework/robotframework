from robot.api import Failure, Error


def failure(msg='I failed my duties'):
    raise Failure(msg)


def error(msg='I errored my duties'):
    raise Error(msg)
