"""Simple example how to call c code from Robot Framework.

C code can be used with RF if is compiled as shared library.
"""

__version__=0.01

import ctypes


class PasswordValidator:

    def __init__(self, library):
        self._lib = ctypes.CDLL(library)

    def check_user(self, username, password):
	""" Validates user name and password using imported shared C library.
	"""
        return self._lib.check_password(username, password)


