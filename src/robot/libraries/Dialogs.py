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


"""A test library providing dialogs for interacting with users.

`Dialogs` is Robot Framework's standard library that provides means
for pausing the test execution and getting input from users. The
dialogs are slightly different depending on are tests run on Python or
Jython but they provide the same functionality.
"""

import sys

try:
    from robot import utils
except ImportError:
    __version__ = 'unknown'
else:
    __version__ = utils.get_version()


DIALOG_TITLE = 'Robot Framework'


def pause_execution(message='Test execution paused. Press OK to continue.'):
    """Pauses the test execution and shows dialog with the text `message`. """
    _pause_execution(message)

def execute_manual_step(message, default_error=''):
    """Pauses the test execution until user sets the keyword status.

    `message` is the instruction shown in the dialog. User can select
    PASS or FAIL, and in the latter case an additional dialog is
    opened for defining the error message. `default_error` is the
    possible default value shown in the error message dialog.
    """
    if not _execute_manual_step(message, default_error):
        msg = get_value_from_user('Give error message:', default_error)
        raise AssertionError(msg)

def get_value_from_user(message, default_value=''):
    """Pauses the test execution and asks user to input a value.

    `message` is the instruction shown in the dialog. `default_value` is the
    possible default value shown in the input field.
    """
    value = _get_value_from_user(message, default_value)
    if value is None:
        raise ValueError('No value provided by user')    
    return value


if sys.platform.startswith('java'):

    from javax.swing.JOptionPane import showMessageDialog, showOptionDialog, \
        showInputDialog, YES_NO_OPTION, PLAIN_MESSAGE


    def _pause_execution(message):
        showMessageDialog(None, message, DIALOG_TITLE, PLAIN_MESSAGE)

    def _execute_manual_step(message, default_error):
        status = showOptionDialog(None, message, DIALOG_TITLE, YES_NO_OPTION,
                                  PLAIN_MESSAGE, None, ['PASS', 'FAIL'], None)
        return status == 0

    def _get_value_from_user(message, default):
        return showInputDialog(None, message, DIALOG_TITLE, PLAIN_MESSAGE,
                               None, None, default)

else:

    from Tkinter import Tk
    import tkMessageBox
    import tkSimpleDialog
    
    Tk().withdraw() # Hides the main frame.


    def _pause_execution(message):
        tkMessageBox.showinfo(DIALOG_TITLE, message)

    def _execute_manual_step(message, default_error):
        message += '\n\n<Yes> means PASS and <No> means FAIL.'
        return tkMessageBox.askyesno(DIALOG_TITLE, message)

    def _get_value_from_user(message, default):
        return tkSimpleDialog.askstring(DIALOG_TITLE, message,
                                        initialvalue=default)
