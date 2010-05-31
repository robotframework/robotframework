#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
    from robot.version import get_version
except ImportError:
    __version__ = 'unknown'
else:
    __version__ = get_version()


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
    if not  PassFailDialog(message).result:
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
        raise ValueError('No value provided by user')
    return value


if not sys.platform.startswith('java'):

    from Tkinter import Tk, Toplevel, Frame, Listbox, Label, Button,\
                        BOTH, END, LEFT
    import tkMessageBox
    import tkSimpleDialog


    class _AbstractTkDialog(Toplevel):

        def __init__(self, title):
            parent = Tk()
            parent.withdraw()
            Toplevel.__init__(self, parent)
            self._init_dialog(parent, title)
            self._create_body()
            self._create_buttons()
            self.result = None
            self._initial_focus.focus_set()
            self.wait_window(self)

        def _init_dialog(self, parent, title):
            self.title(title)
            self.grab_set()
            self.protocol("WM_DELETE_WINDOW", self._right_clicked)
            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                      parent.winfo_rooty()+50))

        def _create_body(self):
            frame = Frame(self)
            self._initial_focus = self.create_components(frame)
            frame.pack(padx=5, pady=5, expand=1, fill=BOTH)

        def _create_buttons(self):
            frame = Frame(self)
            self._create_button(frame, self._left_button, self._left_clicked)
            self._create_button(frame, self._right_button, self._right_clicked)
            self.bind("<Escape>", self._right_clicked)
            frame.pack()

        def _create_button(self, parent, label, command):
            w = Button(parent, text=label, width=10, command=command)
            w.pack(side=LEFT, padx=5, pady=5)

        def _left_clicked(self, event=None):
            if not self.validate():
                self._initial_focus.focus_set()
                return
            self.withdraw()
            self.apply()
            self.destroy()

        def _right_clicked(self, event=None):
            self.destroy()

        def create_components(self, parent):
            raise NotImplementedError()

        def validate(self):
            raise NotImplementedError()

        def apply(self):
            raise NotImplementedError()


    class MessageDialog:

        def __init__(self, message):
            Tk().withdraw()
            tkMessageBox.showinfo(DIALOG_TITLE, message)


    class InputDialog:

        def __init__(self, message, default):
            Tk().withdraw()
            self.result = tkSimpleDialog.askstring(DIALOG_TITLE, message,
                                                   initialvalue=default)


    class SelectionDialog(_AbstractTkDialog):
        _left_button = 'OK'
        _right_button = 'Cancel'

        def __init__(self, message, values):
            self._message = message
            self._values = values
            _AbstractTkDialog.__init__(self, "Select one option")

        def create_components(self, parent):
            Label(parent, text=self._message).pack(fill=BOTH)
            self._listbox = Listbox(parent)
            self._listbox.pack(fill=BOTH)
            for item in self._values:
                self._listbox.insert(END, item)
            return self._listbox

        def validate(self):
            return bool(self._listbox.curselection())

        def apply(self):
            self.result = self._listbox.get(self._listbox.curselection())


    class PassFailDialog(_AbstractTkDialog):
        _left_button = 'PASS'
        _right_button = 'FAIL'

        def __init__(self, message):
            self._message = message
            _AbstractTkDialog.__init__(self, DIALOG_TITLE)

        def create_components(self, parent):
            label = Label(parent, text=self._message)
            label.pack(fill=BOTH)
            return label

        def validate(self):
            return True

        def apply(self):
            self.result = True


else:

    import time
    from javax.swing import JOptionPane
    from javax.swing.JOptionPane import PLAIN_MESSAGE, UNINITIALIZED_VALUE, \
        YES_NO_OPTION, OK_CANCEL_OPTION, DEFAULT_OPTION


    class _AbstractSwingDialog:

        def __init__(self, message):
            self.result = self._show_dialog(message)

        def _show_dialog(self, message):
            self._init_dialog(message)
            self._show_dialog_and_wait_it_to_be_closed()
            return self._get_value()

        def _show_dialog_and_wait_it_to_be_closed(self):
            dialog = self._pane.createDialog(None, DIALOG_TITLE)
            dialog.setModal(0);
            dialog.show()
            while dialog.isShowing():
                time.sleep(0.2)
            dialog.dispose()

        def _get_value(self):
            value = self._pane.getInputValue()
            if value == UNINITIALIZED_VALUE:
                return None
            return value


    class MessageDialog(_AbstractSwingDialog):

        def _init_dialog(self, message):
            self._pane = JOptionPane(message, PLAIN_MESSAGE, DEFAULT_OPTION)


    class InputDialog(_AbstractSwingDialog):

        def __init__(self, message, default):
            self._default = default
            _AbstractSwingDialog.__init__(self, message)

        def _init_dialog(self, message):
            self._pane = JOptionPane(message, PLAIN_MESSAGE, OK_CANCEL_OPTION)
            self._pane.setWantsInput(True)
            self._pane.setInitialSelectionValue(self._default)


    class SelectionDialog(_AbstractSwingDialog):

        def __init__(self, message, options):
            self._options = options
            _AbstractSwingDialog.__init__(self, message)

        def _init_dialog(self, message):
            self._pane = JOptionPane(message, PLAIN_MESSAGE, OK_CANCEL_OPTION)
            self._pane.setWantsInput(True)
            self._pane.setSelectionValues(self._options)


    class PassFailDialog(_AbstractSwingDialog):

        def _init_dialog(self, message):
            self._buttons = ['PASS', 'FAIL']
            self._pane = JOptionPane(message, PLAIN_MESSAGE, YES_NO_OPTION,
                                     None, self._buttons, 'PASS')

        def _get_value(self):
            value = self._pane.getValue()
            if value in self._buttons and self._buttons.index(value) == 0:
                return True
            return False
