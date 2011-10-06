#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

Note: Dialogs library cannot be used with timeouts on Windows with Python.
"""

__all__ = ['execute_manual_step', 'get_value_from_user',
           'get_selection_from_user', 'pause_execution']

import sys

try:
    from robot.version import get_version as _get_version
except ImportError:
    __version__ = 'unknown'
else:
    __version__ = _get_version()


DIALOG_TITLE = 'Robot Framework'


def pause_execution(message='Test execution paused. Press OK to continue.'):
    """Pauses the test execution and shows dialog with the text `message`. """
    MessageDialog(message)


def execute_manual_step(message, default_error=''):
    """Pauses the test execution until user sets the keyword status.

    `message` is the instruction shown in the dialog. User can select
    PASS or FAIL, and in the latter case an additional dialog is
    opened for defining the error message. `default_error` is the
    possible default value shown in the error message dialog.
    """
    if not PassFailDialog(message).result:
        msg = get_value_from_user('Give error message:', default_error)
        raise AssertionError(msg)


def get_value_from_user(message, default_value=''):
    """Pauses the test execution and asks user to input a value.

    `message` is the instruction shown in the dialog. `default_value` is the
    possible default value shown in the input field. Selecting 'Cancel' fails
    the keyword.
    """
    return _validate_user_input(InputDialog(message, default_value).result)


def get_selection_from_user(message, *values):
    """Pauses the test execution and asks user to select value

    `message` is the instruction shown in the dialog. and `values` are
    the options given to the user. Selecting 'Cancel' fails the keyword.

    This keyword was added into Robot Framework 2.1.2.
    """
    return _validate_user_input(SelectionDialog(message, values).result)


def _validate_user_input(value):
    if value is None:
        raise RuntimeError('No value provided by user')
    return value


if not sys.platform.startswith('java'):

    from Tkinter import (Tk, Toplevel, Frame, Listbox, Label, Button, Entry,
                         BOTH, END, LEFT, W)
    import tkMessageBox
    import tkSimpleDialog
    from threading import currentThread


    class _AbstractTkDialog(Toplevel):
        _left_button = 'OK'
        _right_button = 'Cancel'

        def __init__(self, message, *args):
            self._prevent_execution_with_timeouts()
            Toplevel.__init__(self, self._get_parent())
            self._init_dialog()
            self._create_body(message, args)
            self._create_buttons()
            self.wait_window(self)

        def _prevent_execution_with_timeouts(self):
            if 'linux' not in sys.platform \
                    and currentThread().getName() != 'MainThread':
                raise RuntimeError('Dialogs library is not supported with '
                                   'timeouts on Python on this platform.')

        def _get_parent(self):
            parent = Tk()
            parent.withdraw()
            return parent

        def _init_dialog(self):
            self.title(DIALOG_TITLE)
            self.grab_set()
            self.protocol("WM_DELETE_WINDOW", self._right_button_clicked)
            self.bind("<Escape>", self._right_button_clicked)
            self.minsize(250, 80)
            self.geometry("+%d+%d" % self._get_center_location())

        def _get_center_location(self):
            x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 2
            y = (self.winfo_screenheight() - self.winfo_reqheight()) / 2
            return x, y

        def _create_body(self, message, args):
            frame = Frame(self)
            Label(frame, text=message, anchor=W, justify=LEFT).pack(fill=BOTH)
            selector = self._create_selector(frame, *args)
            if selector:
                selector.pack(fill=BOTH)
                selector.focus_set()
            frame.pack(padx=5, pady=5, expand=1, fill=BOTH)

        def _create_selector(self, frame):
            return None

        def _create_buttons(self):
            frame = Frame(self)
            self._create_button(frame, self._left_button,
                                self._left_button_clicked)
            self._create_button(frame, self._right_button,
                                self._right_button_clicked)
            frame.pack()

        def _create_button(self, parent, label, callback):
            if label:
                button = Button(parent, text=label, width=10, command=callback)
                button.pack(side=LEFT, padx=5, pady=5)

        def _left_button_clicked(self, event=None):
            if self._validate_value():
                self.result = self._get_value()
                self.destroy()

        def _get_value(self):
            return None

        def _validate_value(self):
            return True

        def _right_button_clicked(self, event=None):
            self.result = self._get_right_button_value()
            self.destroy()

        def _get_right_button_value(self):
            return None


    class MessageDialog(_AbstractTkDialog):
        _right_button = None


    class InputDialog(_AbstractTkDialog):

        def __init__(self, message, default=''):
            _AbstractTkDialog.__init__(self, message, default)

        def _create_selector(self, parent, default):
            self._entry = Entry(parent)
            self._entry.insert(0, default)
            self._entry.select_range(0, END)
            return self._entry

        def _get_value(self):
            return self._entry.get()


    class SelectionDialog(_AbstractTkDialog):

        def __init__(self, message, values):
            _AbstractTkDialog.__init__(self, message, values)

        def _create_selector(self, parent, values):
            self._listbox = Listbox(parent)
            for item in values:
                self._listbox.insert(END, item)
            return self._listbox

        def _validate_value(self):
            return bool(self._listbox.curselection())

        def _get_value(self):
            return self._listbox.get(self._listbox.curselection())


    class PassFailDialog(_AbstractTkDialog):
        _left_button = 'PASS'
        _right_button = 'FAIL'

        def _get_value(self):
            return True

        def _get_right_button_value(self):
            return False


else:

    import time
    from javax.swing import JOptionPane
    from javax.swing.JOptionPane import PLAIN_MESSAGE, UNINITIALIZED_VALUE, \
        YES_NO_OPTION, OK_CANCEL_OPTION, DEFAULT_OPTION


    class _AbstractSwingDialog:

        def __init__(self, pane):
            self._show_dialog(pane)
            self.result = self._get_value(pane)

        def _show_dialog(self, pane):
            dialog = pane.createDialog(None, DIALOG_TITLE)
            dialog.setModal(False)
            dialog.show()
            while dialog.isShowing():
                time.sleep(0.2)
            dialog.dispose()

        def _get_value(self, pane):
            value = pane.getInputValue()
            return value if value != UNINITIALIZED_VALUE else None


    class MessageDialog(_AbstractSwingDialog):

        def __init__(self, message):
            pane = JOptionPane(message, PLAIN_MESSAGE, DEFAULT_OPTION)
            _AbstractSwingDialog.__init__(self, pane)


    class InputDialog(_AbstractSwingDialog):

        def __init__(self, message, default):
            pane = JOptionPane(message, PLAIN_MESSAGE, OK_CANCEL_OPTION)
            pane.setWantsInput(True)
            pane.setInitialSelectionValue(default)
            _AbstractSwingDialog.__init__(self, pane)


    class SelectionDialog(_AbstractSwingDialog):

        def __init__(self, message, options):
            pane = JOptionPane(message, PLAIN_MESSAGE, OK_CANCEL_OPTION)
            pane.setWantsInput(True)
            pane.setSelectionValues(options)
            _AbstractSwingDialog.__init__(self, pane)


    class PassFailDialog(_AbstractSwingDialog):

        def __init__(self, message):
            pane = JOptionPane(message, PLAIN_MESSAGE, YES_NO_OPTION,
                               None, ['PASS', 'FAIL'], 'PASS')
            _AbstractSwingDialog.__init__(self, pane)

        def _get_value(self, pane):
            return pane.getValue() == 'PASS'
