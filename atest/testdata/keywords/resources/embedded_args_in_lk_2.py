from robot.api import logger
from robot.api.deco import keyword


@keyword(name="${a}*lib*${b}")
def mult_match3(a, b):
    logger.info(f"{a}*lib*{b}")
