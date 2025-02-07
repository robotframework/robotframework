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
                     Toplevel, W, Canvas)
from typing import Any, Union


class TkDialog(Toplevel):
    left_button = 'OK'
    right_button = 'Cancel'

    def __init__(self, message, value=None, **config):
        self.bg_color = "#232627"   # Dialog background color
        self.button_normal_color ="#009A91"
        self.button_hover_color = "#1AB4A4"
        self.button_click_color = "#009A91"
        self.button_text_color = "white"
        self.button_radius = 7
        self.button_width = 130
        self.button_height = 40
        self.text_font = ("Arial", 11)
        self.button_font = ("Arial", 10, "bold")
        self.input_bg_color = "#6B7376"
        self.input_fg_color = "white"
        self.lable_fg_color = "white"

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
        if sys.platform.startswith("linux"):
            root.wait_visibility(root)
            root.attributes('-alpha', 0)
        if sys.platform.startswith("win"):
            root.withdraw()
        return root

    def _initialize_dialog(self):
        self.withdraw()
        self.configure(bg=self.bg_color)
        self.overrideredirect(True)  

        # Create a custom title bar
        title_bar = Frame(self, bg=self.bg_color, relief="flat", bd=2)
        title_bar.pack(fill="x")
        # Add a title label
        title_label = Label(title_bar, text="Robot Framework - Dialogs", fg="white", bg=self.bg_color, font=("Arial", 10, "bold"))
        title_label.pack(side=LEFT, padx=10,pady=10)
        # Enable dragging functionality
        for widget in (title_bar, title_label):
            widget.bind("<ButtonPress-1>", self._start_move)
            widget.bind("<B1-Motion>", self._on_move)
                
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Escape>", self._close)
        if self.left_button == TkDialog.left_button:
            self.bind("<Return>", self._left_button_clicked)

    # Enable Dragging Functions
    def _start_move(self, event):
        """ Records the initial mouse position when clicking the title bar. """
        self.x_offset = event.x
        self.y_offset = event.y

    def _on_move(self, event):
        """ Moves the window when dragging the title bar. """
        x = self.winfo_x() + (event.x - self.x_offset)
        y = self.winfo_y() + (event.y - self.y_offset)
        self.geometry(f"+{x}+{y}")

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
        frame = Frame(self, bg=self.bg_color)
        max_width = self.winfo_screenwidth() // 2
        label = Label(frame, text=message, anchor=W, justify=LEFT, wraplength=max_width,
                      bg=self.bg_color, fg=self.lable_fg_color, font=self.text_font)
        label.pack(fill=BOTH)
        widget = self._create_widget(frame, value, **config)
        if widget:
            widget.pack(fill=BOTH)
        frame.pack(padx=5, pady=5, expand=1, fill=BOTH)
        return widget

    def _create_widget(self, frame, value) -> Union[Entry, Listbox, None]:
        return None

    def _create_buttons(self):
        frame = Frame(self, bg=self.bg_color)
        self._create_button(frame, self.left_button, self._left_button_clicked)
        self._create_button(frame, self.right_button, self._right_button_clicked)
        frame.pack(pady=10)

    def _create_button(self, parent, label, callback):
        if label:
            frame = Frame(parent, bg=self.bg_color)
            frame.pack(side=LEFT, padx=10, pady=10)

            canvas = Canvas(frame, width=self.button_width, height=self.button_height,
                            bg=self.bg_color, highlightthickness=0)
            canvas.pack()

            x0, y0, x1, y1 = 5, 5, self.button_width - 5, self.button_height - 5

            rounded_rect = [
                canvas.create_oval(x0, y0, x0 + self.button_radius, y0 + self.button_radius,
                                   fill=self.button_normal_color, outline=self.button_normal_color),
                canvas.create_oval(x1 - self.button_radius, y0, x1, y0 + self.button_radius,
                                   fill=self.button_normal_color, outline=self.button_normal_color),
                canvas.create_oval(x0, y1 - self.button_radius, x0 + self.button_radius, y1,
                                   fill=self.button_normal_color, outline=self.button_normal_color),
                canvas.create_oval(x1 - self.button_radius, y1 - self.button_radius, x1, y1,
                                   fill=self.button_normal_color, outline=self.button_normal_color),
                canvas.create_rectangle(x0 + self.button_radius // 2, y0, x1 - self.button_radius // 2, y1,
                                        fill=self.button_normal_color, outline=self.button_normal_color),
                canvas.create_rectangle(x0, y0 + self.button_radius // 2, x1, y1 - self.button_radius // 2,
                                        fill=self.button_normal_color, outline=self.button_normal_color)
            ]

            button = Button(frame, text=label, font=self.button_font,
                            bg=self.button_normal_color, fg=self.button_text_color,
                            activebackground=self.button_normal_color, activeforeground="white",
                            borderwidth=0, relief="flat", cursor="hand2",
                            highlightthickness=0, bd=0,
                            command=callback)

            button_window = canvas.create_window(self.button_width // 2, self.button_height // 2,
                                                 window=button, width=100, height=30)

            def on_hover(event):
                for shape in rounded_rect:
                    canvas.itemconfig(shape, fill=self.button_hover_color, outline=self.button_hover_color)
                button.config(bg=self.button_hover_color, activebackground=self.button_hover_color)

            def on_leave(event):
                for shape in rounded_rect:
                    canvas.itemconfig(shape, fill=self.button_normal_color, outline=self.button_normal_color)
                button.config(bg=self.button_normal_color, activebackground=self.button_normal_color)

            def on_click(event):
                for shape in rounded_rect:
                    canvas.itemconfig(shape, fill=self.button_click_color, outline=self.button_click_color)
                button.config(bg=self.button_click_color, activebackground=self.button_click_color)

            def on_release(event):
                on_hover(event)  # Restore hover color after click

            button.bind("<Enter>", on_hover)
            button.bind("<Leave>", on_leave)
            button.bind("<ButtonPress-1>", on_click)
            button.bind("<ButtonRelease-1>", on_release)

            canvas.bind("<Enter>", on_hover)
            canvas.bind("<Leave>", on_leave)
            canvas.bind("<ButtonPress-1>", on_click)
            canvas.bind("<ButtonRelease-1>", on_release)

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
        # Create a wrapper frame to control spacing
        input_frame = Frame(parent, bg=self.bg_color)
        input_frame.pack(pady=5)  # Adjust this value to increase/decrease spacing
        # Create the Entry widget inside the frame
        widget = Entry(input_frame, bg=self.input_bg_color,fg=self.input_fg_color, show='*' if hidden else '')
        widget.pack(ipadx=70,ipady=5,padx=5, pady=10)  # Adds some internal padding for spacing

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
        widget = Listbox(parent,background=self.input_bg_color)
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
        widget = Listbox(parent, background=self.input_bg_color, selectmode='multiple')
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
