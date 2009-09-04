
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


from ctypes import CDLL, c_char_p


LIBRARY = CDLL('./libpasswordvalidatorstub.so.1.0.0')


def check_user(username, password):
    """ Validates user name and password using imported shared C library."""
    if not LIBRARY.validate_user(c_char_p(username), c_char_p(password)):
        raise AssertionError('Wrong username/password combination')


if __name__ == '__main__':
    import sys
    try:
        check_user(*sys.argv[1:])
    except AssertionError, err:
        print err
    except TypeError:
        print 'Usage:  %s username password' % sys.argv[0]
    else:
        print 'Valid password'
