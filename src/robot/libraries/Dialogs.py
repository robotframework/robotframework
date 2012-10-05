#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

"""A test library providing dialogs for interacting with users.

`Dialogs` is Robot Framework's standard library that provides means
for pausing the test execution and getting input from users. The
dialogs are slightly different depending on are tests run on Python or
Jython but they provide the same functionality.

The library has following two limitations:
- It is not compatible with IronPython.
- It cannot be used with timeouts on Python.
"""

import sys

if sys.platform.startswith('java'):
    from dialogs_jy import MessageDialog, PassFailDialog, InputDialog, SelectionDialog
elif sys.platform == 'cli':
    from dialogs_ipy import MessageDialog, PassFailDialog, InputDialog, SelectionDialog
else:
    from dialogs_py import MessageDialog, PassFailDialog, InputDialog, SelectionDialog

try:
    from robot.version import get_version
except ImportError:
    __version__ = '<unknown>'
else:
    __version__ = get_version()

__all__ = ['execute_manual_step', 'get_value_from_user',
           'get_selection_from_user', 'pause_execution']


def pause_execution(message='Test execution paused. Press OK to continue.'):
    """Pauses test execution until user clicks `Ok` button.

    `message` is the message shown in the dialog.
    """
    MessageDialog(message).show()


def execute_manual_step(message, default_error=''):
    """Pauses test execution until user sets the keyword status.

    User can select 'PASS' or 'FAIL', and in the latter case an additional
    dialog is opened for defining the error message.

    `message` is the instruction shown in the initial dialog and
    `default_error` is the default value shown in the possible error message
    dialog.
    """
    if not PassFailDialog(message).show():
        msg = get_value_from_user('Give error message:', default_error)
        raise AssertionError(msg)


def get_value_from_user(message, default_value=''):
    """Pauses test execution and asks user to input a value.

    `message` is the instruction shown in the dialog and `default_value` is
    the possible default value shown in the input field. Selecting 'Cancel'
    fails the keyword.
    """
    return _validate_user_input(InputDialog(message, default_value))


def get_selection_from_user(message, *values):
    """Pauses test execution and asks user to select a value.

    `message` is the instruction shown in the dialog and `values` are
    the options given to the user. Selecting 'Cancel' fails the keyword.
    """
    return _validate_user_input(SelectionDialog(message, values))


def _validate_user_input(dialog):
    value = dialog.show()
    if value is None:
        raise RuntimeError('No value provided by user')
    return value
