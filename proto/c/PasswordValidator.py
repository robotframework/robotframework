
#  Copyright 2009 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


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
        if not self._lib.validate_user(c_char_p(username), c_char_p(password)):
            raise AssertionError('Wrong username/password combination')


