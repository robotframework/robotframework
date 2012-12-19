import os

HOST = 'localhost'
USERNAME = 'test'
PASSWORD = 'test'
FULL_PROMPT = '%s@%s ~ $ ' % (USERNAME, os.uname()[1])
PROMPT_START = '%s@' % USERNAME
HOME = '/home/%s' % USERNAME
