import os

HOST = 'localhost'
USERNAME = 'test'
PASSWORD = 'test'
MACHINE = os.uname()[1]
FULL_PROMPT = '[%s@%s ~]$' % (USERNAME, MACHINE)

pwd = u'pwd'
pwd_amp = u'pwd &'
unic_string = u'Hyv\u00E4\u00E4 \u00FC\u00F6t\u00E4'

