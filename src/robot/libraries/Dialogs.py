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
    possible default value shown in the input field. Selecting 'Cancel' fails 
    the keyword.
    """
    value = _get_value_from_user(message, default_value)
    if value is None:
        raise ValueError('No value provided by user')    
    return value

def get_selection_from_user(message, *values):
    """Pauses the test execution and asks user to select value

    `message` is the instruction shown in the dialog. and `values` are 
    the options given to the user. Selecting 'Cancel' fails the keyword.
    """
    value = _get_selection_from_user(message, values)
    if value is None:
        raise ValueError('No value provided by user')    
    return value

def _pause_execution(message):
    _MessageDialog(message)

def _execute_manual_step(message):
    return _PassFailDialog(message).result

def _get_value_from_user(message, default):
    return _InputDialog(message, default).result

def _get_selection_from_user(message, values):
    return _SelectionDialog(message, list(values)).result


if not sys.platform.startswith('java'):
    # CPython implementation

    from Tkinter import Tk, Toplevel, Frame, Listbox, Label, Button,\
                        BOTH, END, ACTIVE, LEFT
    import tkMessageBox
    import tkSimpleDialog
    
    # Hides the main frame when tkMessageBox and tkSimpleDialog is used
    Tk().withdraw() 


    class _AbstractTkDialog(Toplevel):
    
        def __init__(self, title):
            parent = Tk()
            parent.withdraw() # Hides the main frame.
            Toplevel.__init__(self, parent)
            self.title(title)
            self.parent = parent
            self.result = None
            body = Frame(self)
            self.initial_focus = self.body(body)
            body.pack(padx=5, pady=5, expand=1, fill=BOTH)
            self.buttonbox()
            self.grab_set()
            if not self.initial_focus:
                self.initial_focus = self
            self.protocol("WM_DELETE_WINDOW", self._right_clicked)
            self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
            parent.winfo_rooty()+50))
            self.initial_focus.focus_set()
            self.wait_window(self)
    
        def buttonbox(self):
            box = Frame(self)
            w = Button(box, text=self._left_button, width=10, command=self._left_clicked, default=ACTIVE)
            w.pack(side=LEFT, padx=5, pady=5)
            w = Button(box, text=self._right_button, width=10, command=self._right_clicked)
            w.pack(side=LEFT, padx=5, pady=5)
            self.bind("&lt;Return>", self._left_clicked)
            self.bind("&lt;Escape>", self._right_clicked)
            box.pack()
    
        def _left_clicked(self, event=None):
            if not self.validate():
                self.initial_focus.focus_set()
                return
            self.withdraw()
            self.update_idletasks()
            self.apply()
            self._right_clicked()
    
        def _right_clicked(self, event=None):
            self.parent.focus_set()
            self.destroy()
    
        def body(self, parent):
            raise NotImplementedError()

        def validate(self):
            raise NotImplementedError()

        def apply(self):
            raise NotImplementedError()


    class _MessageDialog:

        def __init__(self, message):
            tkMessageBox.showinfo(DIALOG_TITLE, message)


    class _InputDialog:

        def __init__(self, message, default):
            self.result = tkSimpleDialog.askstring(DIALOG_TITLE, message,
                                                   initialvalue=default)


    class _SelectionDialog(_AbstractTkDialog):
        _left_button = 'OK'
        _right_button = 'Cancel'

        def __init__(self, message, values):
            self._message = message
            self._values = values
            _AbstractTkDialog.__init__(self, "Select one option")

        def body(self, parent):
            Label(parent, text=self._message).pack(fill=BOTH)
            self._listbox = Listbox(parent)
            self._listbox.pack(fill=BOTH)
            for item in self._values:
                self._listbox.insert(END, item)
            return self._listbox

        def validate(self):
            return self._listbox.curselection()

        def apply(self):
            self.result = self._listbox.get(self._listbox.curselection())


    class _PassFailDialog(_AbstractTkDialog):
        _left_button = 'PASS'
        _right_button = 'FAIL'

        def __init__(self, message):
            self._message = message
            _AbstractTkDialog.__init__(self, DIALOG_TITLE)

        def body(self, parent):
            Label(parent, text=self._message).pack(fill=BOTH)

        def validate(self):
            return True

        def apply(self):
            self.result = True


else:
    # Jython implementation

    import time
    from javax.swing import JOptionPane
    from javax.swing.JOptionPane import PLAIN_MESSAGE, UNINITIALIZED_VALUE, \
        YES_NO_OPTION, OK_CANCEL_OPTION, DEFAULT_OPTION


    class _AbstractSwingDialog:

        def __init__(self, message):
            self._message = message
            self.result = self._show_dialog()

        def _show_dialog(self):
            self._create_pane()
            self._create_dialog_and_wait_it_to_be_closed()
            return self._get_value()
    
        def _create_dialog_and_wait_it_to_be_closed(self):
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


    class _MessageDialog(_AbstractSwingDialog):

        def _create_pane(self):
            self._pane = JOptionPane(self._message, PLAIN_MESSAGE,
                                     DEFAULT_OPTION)


    class _InputDialog(_AbstractSwingDialog):

        def __init__(self, message, default):
            self._default = default
            _AbstractSwingDialog.__init__(self, message)

        def _create_pane(self):
            self._pane = JOptionPane(self._message, PLAIN_MESSAGE, 
                                     OK_CANCEL_OPTION)
            self._pane.setWantsInput(True)
            self._pane.setInitialSelectionValue(self._default)

    class _SelectionDialog(_AbstractSwingDialog):

        def __init__(self, message, options):
            self._options = options
            _AbstractSwingDialog.__init__(self, message)

        def _create_pane(self):
            self._pane = JOptionPane(self._message, PLAIN_MESSAGE, 
                                     OK_CANCEL_OPTION)
            self._pane.setWantsInput(True)
            self._pane.setSelectionValues(self._options)


    class _PassFailDialog(_AbstractSwingDialog):

        def _create_pane(self):
            self._buttons = ['PASS', 'FAIL']
            self._pane = JOptionPane(self._message, PLAIN_MESSAGE, YES_NO_OPTION,
                                     None, self._buttons, 'PASS')

        def _get_value(self):
            value = self._pane.getValue()
            if value in self._buttons and self._buttons.index(value) == 0:
                return True
            return False

