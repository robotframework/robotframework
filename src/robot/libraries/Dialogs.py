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


"""Dialogs is a test library that provides means for pausing the test execution
and asking for user input"""


def pause_execution(message='Test execution paused. Press OK to continue.'):
    """Pauses the test execution and shows dialog with text `message`. """
    _pause_execution(message)

def execute_manual_step(message='Set keyword status', error='Execution failed'):
    """Pauses the test execution and shows a dialog with text `message`.

    User can choose to pass or fail the test. In case of failing the test,
    additional dialog is opened for defining the error message. `error` is the
    default error message.
    """
    _execute_manual_step(message, error)

def get_value_from_user(message='Give value:', default=''):
    """Pauses the test execution and asks user to input value.

    `message` is the instruction to user. `default` is the default value of the
    input field.
    """
    return _get_value_from_user(message, default)


import sys
DIALOG_TITLE = 'Robot Framework'

if sys.platform.startswith('java'):

    from javax.swing.JOptionPane import showMessageDialog, showOptionDialog,\
        showInputDialog, YES_NO_OPTION, PLAIN_MESSAGE


    def _pause_execution(message):
        showMessageDialog(None, message, DIALOG_TITLE, PLAIN_MESSAGE)

    def _execute_manual_step(message, error):
        status = showOptionDialog(None, message, DIALOG_TITLE, YES_NO_OPTION,
                                  PLAIN_MESSAGE, None, ['PASS', 'FAIL'], None)
        if status != 0:
            msg = _get_value_from_user('Give error message:', 'Failed') 
            raise AssertionError(msg)

    def _get_value_from_user(message, default):
        value = showInputDialog(None, message, DIALOG_TITLE, PLAIN_MESSAGE,
                                None, None, default)
        if value is None:
            raise ValueError('No value provided by user')    
        return value


else:

    from Tkinter import Tk
    import tkMessageBox
    import tkSimpleDialog
    
    Tk().withdraw() # Hides the main frame.


    def _pause_execution(message):
        tkMessageBox.showinfo(DIALOG_TITLE, message)

    def _execute_manual_step(message, error):
        message += '\n\nYes means PASS, No means FAIL'
        if not tkMessageBox.askyesno(DIALOG_TITLE, message):
            msg = _get_value_from_user('Give error message:', 'Failed')
            raise AssertionError(msg)

    def _get_value_from_user(message, default):
        value = tkSimpleDialog.askstring(DIALOG_TITLE, message, initialvalue=default)
        if value is None:
            raise ValueError('No value provided by user')    
        return value

