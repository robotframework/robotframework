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

import time
import tkinter as tk
from importlib.resources import read_binary

from robot.utils import WINDOWS

if WINDOWS:
    # A hack to override the default taskbar icon on Windows. See, for example:
    # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105
    from ctypes import windll

    windll.shell32.SetCurrentProcessExplicitAppUserModelID("robot.dialogs")


class TkDialog(tk.Toplevel):
    left_button = "OK"
    right_button = "Cancel"
    font = (None, 12)
    padding = 8 if WINDOWS else 16
    background = None  # Can be used to change the dialog background.

    def __init__(self, message, value=None, **config):
        super().__init__(self._get_root())
        self._button_bindings = {}
        self._initialize_dialog()
        self.widget = self._create_body(message, value, **config)
        self._create_buttons()
        self._finalize_dialog()
        self._result = None
        self._closed = False

    def _get_root(self) -> tk.Tk:
        root = tk.Tk()
        root.withdraw()
        icon = tk.PhotoImage(master=root, data=read_binary("robot", "logo.png"))
        root.iconphoto(True, icon)
        return root

    def _initialize_dialog(self):
        self.withdraw()  # Remove from display until finalized.
        self.title("Robot Framework")
        self.configure(padx=self.padding, background=self.background)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Escape>", self._close)
        if self.left_button == TkDialog.left_button:
            self.bind("<Return>", self._left_button_clicked)

    def _finalize_dialog(self):
        self.update()  # Needed to get accurate dialog size.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        min_width = screen_width // 5
        min_height = screen_height // 8
        width = max(self.winfo_reqwidth(), min_width)
        height = max(self.winfo_reqheight(), min_height)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.lift()
        self.deiconify()
        if self.widget:
            self.widget.focus_set()

    def _create_body(self, message, value, **config) -> "tk.Entry|tk.Listbox|None":
        frame = tk.Frame(self, background=self.background)
        max_width = self.winfo_screenwidth() // 2
        label = tk.Label(
            frame,
            text=message,
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=max_width,
            pady=self.padding,
            background=self.background,
            font=self.font,
        )
        label.pack(fill=tk.BOTH)
        widget = self._create_widget(frame, value, **config)
        if widget:
            widget.pack(fill=tk.BOTH, pady=self.padding)
        frame.pack(expand=1, fill=tk.BOTH)
        return widget

    def _create_widget(self, frame, value) -> "tk.Entry|tk.Listbox|None":
        return None

    def _create_buttons(self):
        frame = tk.Frame(self, pady=self.padding, background=self.background)
        self._create_button(frame, self.left_button, self._left_button_clicked)
        self._create_button(frame, self.right_button, self._right_button_clicked)
        frame.pack()

    def _create_button(self, parent, label, callback):
        if label:
            button = tk.Button(
                parent,
                text=label,
                command=callback,
                width=10,
                underline=0,
                font=self.font,
            )
            button.pack(side=tk.LEFT, padx=self.padding)
            for char in label[0].upper(), label[0].lower():
                self.bind(char, callback)
                self._button_bindings[char] = callback

    def _left_button_clicked(self, event=None):
        if self._validate_value():
            self._result = self._get_value()
            self._close()

    def _validate_value(self) -> bool:
        return True

    def _get_value(self) -> "str|list[str]|bool|None":
        return None

    def _right_button_clicked(self, event=None):
        self._result = self._get_right_button_value()
        self._close()

    def _get_right_button_value(self) -> "str|list[str]|bool|None":
        return None

    def _close(self, event=None):
        self._closed = True

    def show(self) -> "str|list[str]|bool|None":
        # Use a loop with `update()` instead of `wait_window()` to allow
        # timeouts and signals stop execution.
        try:
            while not self._closed:
                time.sleep(0.1)
                self.update()
        finally:
            self.destroy()
            self.update()  # Needed on Linux to close the dialog (#1466, #4993)
        return self._result


class MessageDialog(TkDialog):
    right_button = None


class InputDialog(TkDialog):

    def __init__(self, message, default="", hidden=False):
        super().__init__(message, default, hidden=hidden)

    def _create_widget(self, parent, default, hidden=False) -> tk.Entry:
        widget = tk.Entry(parent, show="*" if hidden else "", font=self.font)
        widget.insert(0, default)
        widget.select_range(0, tk.END)
        widget.bind("<FocusIn>", self._unbind_buttons)
        widget.bind("<FocusOut>", self._rebind_buttons)
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

    def _create_widget(self, parent, values, default=None) -> tk.Listbox:
        widget = tk.Listbox(parent, font=self.font)
        for item in values:
            widget.insert(tk.END, item)
        if default is not None:
            index = self._get_default_value_index(default, values)
            widget.select_set(index)
            widget.activate(index)
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
            raise ValueError("Default value index is out of bounds.")
        return index

    def _validate_value(self) -> bool:
        return bool(self.widget.curselection())

    def _get_value(self) -> str:
        return self.widget.get(self.widget.curselection())


class MultipleSelectionDialog(TkDialog):

    def _create_widget(self, parent, values) -> tk.Listbox:
        widget = tk.Listbox(parent, selectmode="multiple", font=self.font)
        for item in values:
            widget.insert(tk.END, item)
        widget.config(width=0)
        return widget

    def _get_value(self) -> "list[str]":
        return [self.widget.get(i) for i in self.widget.curselection()]


class PassFailDialog(TkDialog):
    left_button = "PASS"
    right_button = "FAIL"

    def _get_value(self) -> bool:
        return True

    def _get_right_button_value(self) -> bool:
        return False
