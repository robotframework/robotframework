import os, sys
if sys.version_info[0] == 2:
    res = os.getenv('X_X').decode(sys.getfilesystemencoding())
else:
    res = os.getenv('X_X')
print(res == u'hyv\xe4')
