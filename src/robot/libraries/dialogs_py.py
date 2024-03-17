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


class TkDialog(Toplevel):
    left_button = 'OK'
    right_button = 'Cancel'

    def __init__(self, message, value=None, **config):
        self._prevent_execution_with_timeouts()
        self._button_bindings = {}
        super().__init__(self._get_root())
        self._initialize_dialog()
        self.widget = self._create_body(message, value, **config)
        self._create_buttons()
        self._finalize_dialog()
        self._result = None

    def _prevent_execution_with_timeouts(self):
        if 'linux' not in sys.platform and current_thread().name != 'MainThread':
            raise RuntimeError('Dialogs library is not supported with '
                               'timeouts on Python on this platform.')

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

    def _create_widget(self, parent, values) -> Listbox:
        widget = Listbox(parent)
        for item in values:
            widget.insert(END, item)
        widget.config(width=0)
        return widget

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
