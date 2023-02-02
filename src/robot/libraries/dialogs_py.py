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
from tkinter import (BOTH, Button, END, Entry, Frame, Label, LEFT, Listbox,
                     Tk, Toplevel, W, Widget)
from typing import Optional


class TkDialog(Toplevel):
    _left_button = 'OK'
    _right_button = 'Cancel'

    def __init__(self, message, value=None, **config):
        self._prevent_execution_with_timeouts()
        self._parent = self._get_parent()
        super().__init__(self._parent)
        self._initialize_dialog()
        self._create_body(message, value, **config)
        self._create_buttons()
        self._finalize_dialog()
        self._result = None

    def _prevent_execution_with_timeouts(self):
        if 'linux' not in sys.platform and current_thread().name != 'MainThread':
            raise RuntimeError('Dialogs library is not supported with '
                               'timeouts on Python on this platform.')

    def _get_parent(self) -> Tk:
        parent = Tk()
        parent.withdraw()
        return parent

    def _initialize_dialog(self):
        self.withdraw()    # Remove from display until finalized.
        self.title('Robot Framework')
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Escape>", self._close)

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

    def _create_body(self, message, value, **config):
        frame = Frame(self)
        max_width = self.winfo_screenwidth() // 2
        label = Label(frame, text=message, anchor=W, justify=LEFT, wraplength=max_width)
        label.pack(fill=BOTH)
        widget = self._create_widget(frame, value, **config)
        if widget:
            widget.pack(fill=BOTH)
            widget.focus_set()
        frame.pack(padx=5, pady=5, expand=1, fill=BOTH)

    def _create_widget(self, frame, value) -> Optional[Widget]:
        return None

    def _create_buttons(self):
        frame = Frame(self)
        self._create_button(frame, self._left_button, self._left_button_clicked)
        self._create_button(frame, self._right_button, self._right_button_clicked)
        frame.pack()

    def _create_button(self, parent, label, callback):
        if label:
            button = Button(parent, text=label, width=10, command=callback)
            button.pack(side=LEFT, padx=5, pady=5)

    def _left_button_clicked(self, event=None):
        if self._validate_value():
            self._result = self._get_value()
            self._close()

    def _validate_value(self):
        return True

    def _get_value(self):
        return None

    def _close(self, event=None):
        # self.destroy() is not enough on Linux
        self._parent.destroy()

    def _right_button_clicked(self, event=None):
        self._result = self._get_right_button_value()
        self._close()

    def _get_right_button_value(self):
        return None

    def show(self):
        self.wait_window(self)
        return self._result


class MessageDialog(TkDialog):
    _right_button = None


class InputDialog(TkDialog):

    def __init__(self, message, default='', hidden=False):
        super().__init__(message, default, hidden=hidden)

    def _create_widget(self, parent, default, hidden=False):
        self._entry = Entry(parent, show='*' if hidden else '')
        self._entry.insert(0, default)
        self._entry.select_range(0, END)
        return self._entry

    def _get_value(self):
        return self._entry.get()


class SelectionDialog(TkDialog):

    def _create_widget(self, parent, values):
        self._listbox = Listbox(parent)
        for item in values:
            self._listbox.insert(END, item)
        self._listbox.config(width=0)
        return self._listbox

    def _validate_value(self):
        return bool(self._listbox.curselection())

    def _get_value(self):
        return self._listbox.get(self._listbox.curselection())


class MultipleSelectionDialog(TkDialog):

    def _create_widget(self, parent, values):
        self._listbox = Listbox(parent, selectmode='multiple')
        for item in values:
            self._listbox.insert(END, item)
        self._listbox.config(width=0)
        return self._listbox

    def _get_value(self):
        selected_values = [self._listbox.get(i) for i in self._listbox.curselection()]
        return selected_values


class PassFailDialog(TkDialog):
    _left_button = 'PASS'
    _right_button = 'FAIL'

    def _get_value(self):
        return True

    def _get_right_button_value(self):
        return False
