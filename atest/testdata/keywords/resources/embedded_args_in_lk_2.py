from robot.api import logger
from robot.api.deco import keyword


@keyword(name="${a}*lib*${b}")
def mult_match3(a, b):
    logger.info("%s*lib*%s" % (a, b))
