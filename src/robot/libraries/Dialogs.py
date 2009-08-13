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
    if not _execute_manual_step(message):
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


if not sys.platform.startswith('java'):
    # CPython implementation

    from Tkinter import Tk
    import tkMessageBox
    import tkSimpleDialog
    
    Tk().withdraw() # Hides the main frame.


    def _pause_execution(message):
        tkMessageBox.showinfo(DIALOG_TITLE, message)

    def _execute_manual_step(message):
        message += '\n\n<Yes> means PASS and <No> means FAIL.'
        return tkMessageBox.askyesno(DIALOG_TITLE, message)

    def _get_value_from_user(message, default):
        return tkSimpleDialog.askstring(DIALOG_TITLE, message,
                                        initialvalue=default)


else:
    # Jython implementation

    import time
    from javax.swing import JOptionPane
    from javax.swing.JOptionPane import PLAIN_MESSAGE, YES_NO_OPTION, \
        OK_CANCEL_OPTION, DEFAULT_OPTION, UNINITIALIZED_VALUE, CLOSED_OPTION

    def _pause_execution(message):
        _show_dialog(message, PLAIN_MESSAGE)

    def _execute_manual_step(message):
        return 0 == _show_dialog(message, PLAIN_MESSAGE, 
                                 YES_NO_OPTION, ['PASS', 'FAIL'])

    def _get_value_from_user(message, default):
        return _show_dialog(message, PLAIN_MESSAGE, OK_CANCEL_OPTION, 
                            initial_value=default, input=True)

    def _show_dialog(message, message_type, option_type=DEFAULT_OPTION, 
                     options=None, initial_value=None, input=False):
        pane = JOptionPane(message, message_type, option_type, 
                           None, options, initial_value)
        pane.setInitialSelectionValue(initial_value)
        pane.setWantsInput(input)
        _create_dialog_and_wait_it_to_be_closed(pane)
        if input:
            return _get_input_value(pane)
        return _get_selected_button_index(pane, options)

    def _create_dialog_and_wait_it_to_be_closed(pane):
        dialog = pane.createDialog(None, DIALOG_TITLE)
        dialog.setModal(0);
        dialog.show()
        while dialog.isShowing():
            time.sleep(0.2)
        dialog.dispose()

    def _get_input_value(pane):
        value = pane.getInputValue()
        if value == UNINITIALIZED_VALUE:
            return None
        return value

    def _get_selected_button_index(pane, options):
        value = pane.getValue();
        if options is None:
            try:
                return int(value)
            except ValueError, TypeError:
                return CLOSED_OPTION
        if value in options:
            return options.index(value)
        return CLOSED_OPTION

