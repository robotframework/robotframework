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

"""Tk dialog UI for the interactive step debugger.

The dialog is a Tk Toplevel with:

* A message label at the top describing the pause reason.
* A two-pane middle area with a keyword stack on the left and a variables
  table on the right.
* A footer row with five buttons (Step In, Step Over, Step Out, Continue,
  Abort) and matching keyboard shortcuts (I, O, U, C, A; Esc = Continue).

The class mirrors ``dialogs_py.TkDialog`` style — same modal
``show()`` poll loop using ``time.sleep`` + ``update``, same logo icon,
same WINDOWS taskbar workaround.

Used only by ``_debugger._DebugController``. Imported lazily so that
``import robot.libraries.Dialogs`` does not pull in Tk at module-load
time.
"""

import os
import time
import tkinter as tk
from importlib.resources import read_binary
from tkinter import ttk

from robot.utils import WINDOWS

from . import _debugger


if WINDOWS:
    from ctypes import windll

    windll.shell32.SetCurrentProcessExplicitAppUserModelID("robot.dialogs")


_BUTTON_SPECS = (
    ("Step In", _debugger.STEP_IN, ("i", "I")),
    ("Step Over", _debugger.STEP_OVER, ("o", "O")),
    ("Step Out", _debugger.STEP_OUT, ("u", "U")),
    ("Continue", _debugger.CONTINUE, ("c", "C")),
    ("Abort", _debugger.ABORT, ("a", "A")),
)


def check_display_available():
    """Raise a clear error if a graphical display is not available.

    * If ``ROBOT_NO_DIALOGS`` is set to a truthy value (e.g. ``1``,
      ``true``, ``yes``), always refuse to open the dialog. Useful for
      CI runs where we want any stray ``Debug`` keyword to fail fast
      rather than hang waiting for a click.
    * On POSIX, also refuse if neither ``DISPLAY`` nor
      ``WAYLAND_DISPLAY`` are set.
    * On Windows the GUI is always available in an interactive session,
      so we trust ``tk.Tk()`` to surface its own ``TclError`` otherwise.
    """
    if _truthy(os.environ.get("ROBOT_NO_DIALOGS")):
        raise RuntimeError(
            "Cannot open Robot Framework debugger: ROBOT_NO_DIALOGS is set. "
            "Remove the `Debug` keyword or unset the env var to run "
            "interactively."
        )
    if WINDOWS:
        return
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        return
    raise RuntimeError(
        "Cannot open Robot Framework debugger: no graphical display "
        "available. Set DISPLAY (X11) or WAYLAND_DISPLAY (Wayland), or "
        "remove the `Debug` keyword from the test before running headlessly."
    )


def _truthy(value):
    if value is None:
        return False
    return value.strip().lower() not in ("", "0", "false", "no", "off", "none")


class DebuggerDialog(tk.Toplevel):
    """Modal Tk dialog driving the step-debugger UX.

    Constructor parameters mirror the ``dialog_factory`` contract in
    ``_DebugController``. ``show()`` returns one of the action constants
    from ``_debugger`` (``STEP_IN``, ``STEP_OVER``, ``STEP_OUT``,
    ``CONTINUE``, ``ABORT``).
    """

    font = (None, 11)
    mono_font = ("Courier", 10)
    padding = 8 if WINDOWS else 12

    def __init__(self, message, stack, variables, kind="paused"):
        check_display_available()
        super().__init__(self._get_root())
        self._result = None
        self._closed = False
        self._initialize_dialog()
        self._build_body(message, stack, variables)
        self._build_buttons()
        self._finalize_dialog()

    @staticmethod
    def _get_root():
        root = tk.Tk()
        root.withdraw()
        try:
            icon = tk.PhotoImage(master=root, data=read_binary("robot", "logo.png"))
            root.iconphoto(True, icon)
        except Exception:
            pass
        return root

    def _initialize_dialog(self):
        self.withdraw()
        self.title("Robot Framework Debugger")
        self.configure(padx=self.padding, pady=self.padding)
        self.protocol("WM_DELETE_WINDOW", self._on_continue)
        self.bind("<Escape>", self._on_continue)

    def _build_body(self, message, stack, variables):
        header = tk.Label(
            self,
            text=message,
            anchor=tk.W,
            justify=tk.LEFT,
            font=self.font,
            wraplength=600,
        )
        header.pack(fill=tk.X, pady=(0, self.padding))

        panes = tk.Frame(self)
        panes.pack(fill=tk.BOTH, expand=True)

        self._build_stack_panel(panes, stack)
        self._build_variables_panel(panes, variables)

    def _build_stack_panel(self, parent, stack):
        frame = tk.LabelFrame(parent, text="Keyword stack")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, self.padding))
        listbox = tk.Listbox(frame, font=self.mono_font, activestyle="none")
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        for index, frame_text in enumerate(stack):
            listbox.insert(tk.END, f"{index}: {frame_text}")
        if stack:
            listbox.see(tk.END)
            listbox.selection_set(tk.END)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_variables_panel(self, parent, variables):
        frame = tk.LabelFrame(parent, text="Variables")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(
            frame,
            columns=("value",),
            show="tree headings",
            height=12,
        )
        tree.heading("#0", text="Name")
        tree.heading("value", text="Value")
        tree.column("#0", width=180, stretch=False)
        tree.column("value", width=320, stretch=True)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        for name in sorted(variables):
            tree.insert("", tk.END, text=name, values=(variables[name],))
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_buttons(self):
        frame = tk.Frame(self, pady=self.padding)
        frame.pack(fill=tk.X)
        for label, action, shortcuts in _BUTTON_SPECS:
            button = tk.Button(
                frame,
                text=label,
                width=12,
                font=self.font,
                command=self._make_choice(action),
            )
            button.pack(side=tk.LEFT, padx=self.padding // 2)
            for char in shortcuts:
                self.bind(char, self._make_choice(action))

    def _make_choice(self, action):
        def callback(event=None):
            self._result = action
            self._closed = True

        return callback

    def _on_continue(self, event=None):
        self._result = _debugger.CONTINUE
        self._closed = True

    def _finalize_dialog(self):
        self.update()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = max(self.winfo_reqwidth(), screen_width // 2)
        height = max(self.winfo_reqheight(), screen_height // 2)
        width = min(width, screen_width - 40)
        height = min(height, screen_height - 40)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.lift()
        self.deiconify()
        self.focus_force()

    def show(self):
        """Run the dialog modally and return the chosen action.

        Uses the same ``time.sleep`` + ``update`` poll loop as the
        existing Dialogs library so that Robot Framework timeouts and
        signal handlers can still interrupt a paused debugger.
        """
        try:
            while not self._closed:
                time.sleep(0.1)
                self.update()
        finally:
            try:
                self.destroy()
                self.update()
            except tk.TclError:
                pass
        return self._result
