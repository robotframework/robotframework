import os

HOST = 'localhost'
USERNAME = 'test'
PASSWORD = 'test'
MACHINE = os.uname()[1]
FULL_PROMPT = '%s@%s ~ $' % (USERNAME, MACHINE)
PROMPT_START = '%s@' % USERNAME

pwd = u'pwd'
pwd_amp = u'pwd &'
unic_string = u'Hyv\xE4\xE4 \xFC\xF6t\xE4'

