import sys

from robot.api import logger

print("*WARN* Warning via stdout in import")
print("Info via stderr in import", file=sys.stderr)
logger.warn("Warning via API in import")
logger.info("To log and console in import", console=True)
logger.console("Only to console in import")


def keyword():
    pass
