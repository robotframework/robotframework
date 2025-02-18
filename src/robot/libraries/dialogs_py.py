#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

import sys
from threading import current_thread
from tkinter import (BOTH, Button, END, Entry, Frame, Label, LEFT, Listbox, Tk,
                     Toplevel, W)
from typing import Any, Union
from robot.utils import is_truthy

class TkDialog(Toplevel):
    left_button = 'OK'
    right_button = 'Cancel'

    def __init__(self, message, value=None, **config):
        self._button_bindings = {}
        super().__init__(self._get_root())
        self._initialize_dialog()
        self.widget = self._create_body(message, value, **config)
        self._create_buttons()
        self._finalize_dialog()
        self._result = None

    def _get_root(self) -> Tk:
        root = Tk()
        root.withdraw()
        return root

    def _initialize_dialog(self):
        self.withdraw()    # Remove from display until finalized.
        self.title('Robot Framework')
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Escape>", self._close)
        if self.left_button == TkDialog.left_button:
            self.bind("<Return>", self._left_button_clicked)

    def _finalize_dialog(self):
        self.update()    # Needed to get accurate dialog size.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        min_width = screen_width // 6
        min_height = screen_height // 10
        width = max(self.winfo_reqwidth(), min_width)
        height = max(self.winfo_reqheight(), min_height)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.lift()
        self.deiconify()
        if self.widget:
            self.widget.focus_set()

    def _create_body(self, message, value, **config) -> Union[Entry, Listbox, None]:
        frame = Frame(self)
        max_width = self.winfo_screenwidth() // 2
        label = Label(frame, text=message, anchor=W, justify=LEFT, wraplength=max_width)
        label.pack(fill=BOTH)
        widget = self._create_widget(frame, value, **config)
        if widget:
            widget.pack(fill=BOTH)
        frame.pack(padx=5, pady=5, expand=1, fill=BOTH)
        return widget

    def _create_widget(self, frame, value) -> Union[Entry, Listbox, None]:
        return None

    def _create_buttons(self):
        frame = Frame(self)
        self._create_button(frame, self.left_button, self._left_button_clicked)
        self._create_button(frame, self.right_button, self._right_button_clicked)
        frame.pack()

    def _create_button(self, parent, label, callback):
        if label:
            button = Button(parent, text=label, width=10, command=callback, underline=0)
            button.pack(side=LEFT, padx=5, pady=5)
            for char in label[0].upper(), label[0].lower():
                self.bind(char, callback)
                self._button_bindings[char] = callback

    def _left_button_clicked(self, event=None):
        if self._validate_value():
            self._result = self._get_value()
            self._close()

    def _validate_value(self) -> bool:
        return True

    def _get_value(self) -> Any:
        return None

    def _close(self, event=None):
        self.destroy()
        self.update() # Needed on linux to close the window (Issue #1466)

    def _right_button_clicked(self, event=None):
        self._result = self._get_right_button_value()
        self._close()

    def _get_right_button_value(self) -> Any:
        return None

    def show(self) -> Any:
        self.wait_window(self)
        return self._result


class MessageDialog(TkDialog):
    right_button = None


class InputDialog(TkDialog):

    def __init__(self, message, default='', hidden=False):
        super().__init__(message, default, hidden=hidden)

    def _create_widget(self, parent, default, hidden=False) -> Entry:
        widget = Entry(parent, show='*' if hidden else '')
        widget.insert(0, default)
        widget.select_range(0, END)
        widget.bind('<FocusIn>', self._unbind_buttons)
        widget.bind('<FocusOut>', self._rebind_buttons)
        return widget

    def _unbind_buttons(self, event):
        for char in self._button_bindings:
            self.unbind(char)

    def _rebind_buttons(self, event):
        for char, callback in self._button_bindings.items():
            self.bind(char, callback)

    def _get_value(self) -> str:
        return self.widget.get()


class SelectionDialog(TkDialog):

    def __init__(self, message, values, default=None):
        super().__init__(message, values, default=default)

    def _create_widget(self, parent, values, default=None) -> Listbox:
        widget = Listbox(parent)
        for item in values:
            widget.insert(END, item)
        if default is not None:
            widget.select_set(self._get_default_value_index(default, values))
        widget.config(width=0)
        return widget

    def _get_default_value_index(self, default, values) -> int:
        if default in values:
            return values.index(default)
        try:
            index = int(default) - 1
        except ValueError:
            raise ValueError(f"Invalid default value '{default}'.")
        if index < 0 or index >= len(values):
            raise ValueError(f"Default value index is out of bounds.")
        return index

    def _validate_value(self) -> bool:
        return bool(self.widget.curselection())

    def _get_value(self) -> str:
        return self.widget.get(self.widget.curselection())


class MultipleSelectionDialog(TkDialog):

    def _create_widget(self, parent, values) -> Listbox:
        widget = Listbox(parent, selectmode='multiple')
        for item in values:
            widget.insert(END, item)
        widget.config(width=0)
        return widget

    def _get_value(self) -> list:
        selected_values = [self.widget.get(i) for i in self.widget.curselection()]
        return selected_values


class PassFailDialog(TkDialog):
    left_button = 'PASS'
    right_button = 'FAIL'

    def _get_value(self) -> bool:
        return True

    def _get_right_button_value(self) -> bool:
        return False


def pause_execution(message='Execution paused. Press OK to continue.'):
    """Pauses execution until user clicks ``Ok`` button.

    ``message`` is the message shown in the dialog.
    """
    MessageDialog(message).show()


def execute_manual_step(message, default_error=''):
    """Pauses execution until user sets the keyword status.

    User can press either ``PASS`` or ``FAIL`` button. In the latter case execution
    fails and an additional dialog is opened for defining the error message.

    ``message`` is the instruction shown in the initial dialog and
    ``default_error`` is the default value shown in the possible error message
    dialog.
    """
    if not _validate_user_input(PassFailDialog(message)):
        msg = get_value_from_user('Give error message:', default_error)
        raise AssertionError(msg)


def get_value_from_user(message, default_value='', hidden=False):
    """Pauses execution and asks user to input a value.

    Value typed by the user, or the possible default value, is returned.
    Returning an empty value is fine, but pressing ``Cancel`` fails the keyword.

    ``message`` is the instruction shown in the dialog and ``default_value`` is
    the possible default value shown in the input field.

    If ``hidden`` is given a true value, the value typed by the user is hidden.
    ``hidden`` is considered true if it is a non-empty string not equal to
    ``false``, ``none`` or ``no``, case-insensitively. If it is not a string,
    its truth value is got directly using same
    [http://docs.python.org/library/stdtypes.html#truth|rules as in Python].

    Example:
    | ${username} = | Get Value From User | Input user name | default    |
    | ${password} = | Get Value From User | Input password  | hidden=yes |
    """
    return _validate_user_input(InputDialog(message, default_value,
                                            is_truthy(hidden)))


def get_selection_from_user(message, *values, default=None):
    """Pauses execution and asks user to select a value.

    The selected value is returned. Pressing ``Cancel`` fails the keyword.

    ``message`` is the instruction shown in the dialog, ``values`` are
    the options given to the user and ``default`` is the optional default value.

    The default value can either be one of the specified values or the index of
    the value starting from ``1``. For example, ``default=user1`` and ``default=1``
    in the examples below have the exact same effect.

    Example:
    | ${user} = | Get Selection From User | Select user | user1 | user2 | admin |
    | ${user} = | Get Selection From User | Select user | user1 | user2 | admin | default=user1 |
    | ${user} = | Get Selection From User | Select user | user1 | user2 | admin | default=1 |

    ``default`` is new in Robot Framework 7.1.
    """
    return _validate_user_input(SelectionDialog(message, values, default))


def get_selections_from_user(message, *values):
    """Pauses execution and asks user to select multiple values.

    The selected values are returned as a list. Selecting no values is OK
    and in that case the returned list is empty. Pressing ``Cancel`` fails
    the keyword.

    ``message`` is the instruction shown in the dialog and ``values`` are
    the options given to the user.

    Example:
    | ${users} = | Get Selections From User | Select users | user1 | user2 | admin |
    """
    return _validate_user_input(MultipleSelectionDialog(message, values))


def _validate_user_input(dialog):
    value = dialog.show()
    if value is None:
        raise RuntimeError('No value provided by user.')
    return value
