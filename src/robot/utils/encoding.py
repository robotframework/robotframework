import sys
import os

from unic import unic


def encode_to_file_system(string):
    enc = sys.getfilesystemencoding()
    return string.encode(enc) if enc else string

def decode_output(string):
    if _output_encoding:
        return unic(string, _output_encoding)
    return string

def encode_output(string):
    return string.encode(_output_encoding)


def _get_output_encoding():
    encoding = sys.__stdout__.encoding or sys.__stdin__.encoding
    if os.sep == '/':
        return encoding or _read_encoding_from_env()
    # Use default DOS encoding if no encoding found (guess)
    # or on buggy Jython 2.5: http://bugs.jython.org/issue1568
    if not encoding or sys.platform.startswith('java'):
        return 'cp437'
    return encoding

def _read_encoding_from_env():
    for name in 'LANG', 'LC_CTYPE', 'LANGUAGE', 'LC_ALL':
        if name in os.environ:
            return os.environ[name].split('.')[-1]
    return None

_output_encoding = _get_output_encoding()
