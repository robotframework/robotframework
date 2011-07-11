import sys
from robot.api import logger

print '*WARN* Warning via stdout in import'
print >> sys.stderr, 'Info via stderr in import'
logger.warn('Warning via API in import')

def keyword():
    pass
