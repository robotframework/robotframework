"""Robot Framework test library example that calls C code.

This example uses Python's standard `ctypes` module, which requires
that the C code is compiled into a shared library.

It is also possible to execute this file from the command line 
to test the C code manually.
"""

from ctypes import CDLL, c_char_p

LIBRARY = CDLL('./liblogin.so')  # On Windows we'd use '.dll'


def check_user(username, password):
    """Validates user name and password using imported shared C library."""
    if not LIBRARY.validate_user(c_char_p(username), c_char_p(password)):
        raise AssertionError('Wrong username/password combination')


if __name__ == '__main__':
    import sys
    try:
        check_user(*sys.argv[1:])
    except TypeError:
        print 'Usage:  %s username password' % sys.argv[0]
    except AssertionError, err:
        print err
    else:
        print 'Valid password'
