import os

# We assume that prompt is PS1='\u@\h \W \$ '
HOST = 'localhost'
USERNAME = 'test'
PASSWORD = 'test'
PROMPT = '$ '
FULL_PROMPT = '%s@%s ~ $ ' % (USERNAME, os.uname()[1])
PROMPT_START = '%s@' % USERNAME
HOME = '/home/%s' % USERNAME
