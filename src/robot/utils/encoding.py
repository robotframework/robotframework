import sys
import os

from unic import unic


def encode_to_file_system(string):
    return file_system_encoding and string.encode(file_system_encoding) or string

def decode_output(string):
    if output_encoding:
        return unic(string, output_encoding)
    return string

def _read_encoding_from_env():
    if 'LANG' in os.environ:
        return os.environ['LANG'].split('.')[-1]
    if 'LC_CTYPE' in os.environ:
        return os.environ['LC_CTYPE'].split('.')[-1]

file_system_encoding = sys.getfilesystemencoding()
output_encoding = sys.__stdout__.encoding or sys.__stdin__.encoding or \
    _read_encoding_from_env()

