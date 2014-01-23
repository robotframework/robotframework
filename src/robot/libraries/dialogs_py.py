#  Copyright 2008-2014 Nokia Solutions and Networks
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
from threading import currentThread
from Tkinter import (Tk, Toplevel, Frame, Listbox, Label, Button, Entry,
                     BOTH, END, LEFT, W)


class _TkDialog(Toplevel):
    _left_button = 'OK'
    _right_button = 'Cancel'

    def __init__(self, message, value=None, **extra):
        self._prevent_execution_with_timeouts()
        self._parent = self._get_parent()
        Toplevel.__init__(self, self._parent)
        self._initialize_dialog()
        self._create_body(message, value, **extra)
        self._create_buttons()
        self._result = None

    def _prevent_execution_with_timeouts(self):
        if 'linux' not in sys.platform \
                and currentThread().getName() != 'MainThread':
            raise RuntimeError('Dialogs library is not supported with '
                               'timeouts on Python on this platform.')

    def _get_parent(self):
        parent = Tk()
        parent.withdraw()
        return parent

    def _initialize_dialog(self):
        self.title('Robot Framework')
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._right_button_clicked)
        self.bind("<Escape>", self._right_button_clicked)
        self.minsize(250, 80)
        self.geometry("+%d+%d" % self._get_center_location())
        self._bring_to_front()

    def _get_center_location(self):
        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) / 2
        return x, y

    def _bring_to_front(self):
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)

    def _create_body(self, message, value, **extra):
        frame = Frame(self)
        Label(frame, text=message, anchor=W, justify=LEFT, wraplength=800).pack(fill=BOTH)
        selector = self._create_selector(frame, value, **extra)
        if selector:
            selector.pack(fill=BOTH)
            selector.focus_set()
        frame.pack(padx=5, pady=5, expand=1, fill=BOTH)

    def _create_selector(self, frame, value):
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
            self._result = self._get_value()
            self._close()

    def _validate_value(self):
        return True

    def _get_value(self):
        return None

    def _close(self):
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


class MessageDialog(_TkDialog):
    _right_button = None


class InputDialog(_TkDialog):

    def __init__(self, message, default='', hidden=False):
        _TkDialog.__init__(self, message, default, hidden=hidden)

    def _create_selector(self, parent, default, hidden):
        self._entry = Entry(parent, show='*' if hidden else '')
        self._entry.insert(0, default)
        self._entry.select_range(0, END)
        return self._entry

    def _get_value(self):
        return self._entry.get()


class SelectionDialog(_TkDialog):

    def __init__(self, message, values):
        _TkDialog.__init__(self, message, values)

    def _create_selector(self, parent, values):
        self._listbox = Listbox(parent)
        for item in values:
            self._listbox.insert(END, item)
        return self._listbox

    def _validate_value(self):
        return bool(self._listbox.curselection())

    def _get_value(self):
        return self._listbox.get(self._listbox.curselection())


class PassFailDialog(_TkDialog):
    _left_button = 'PASS'
    _right_button = 'FAIL'

    def _get_value(self):
        return True

    def _get_right_button_value(self):
        return False
