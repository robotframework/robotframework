"""Simple example how to call c code from Robot Framework.

C code can be used with RF if is compiled as shared library.
"""

__version__=0.01

from ctypes import CDLL, c_char_p


class PasswordValidator:

    def __init__(self, library):
        self._lib = CDLL(library)

    def check_user(self, username, password):
        """ Validates user name and password using imported shared C library."""
        if not self._lib.check_password(c_char_p(username), c_char_p(password)):
            raise AssertionError('Wrong username/password combination')


