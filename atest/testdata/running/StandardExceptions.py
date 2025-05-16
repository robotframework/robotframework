from robot.api import Error, Failure


def failure(msg="I failed my duties", html=False):
    raise Failure(msg, html)


def error(msg="I errored my duties", html=False):
    raise Error(msg, html=html)
