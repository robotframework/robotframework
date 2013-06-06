#!/usr/bin/env python

#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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


"""Robot Framework Debugfile Viewer

Usage:  fileviever.py [path]

This tool is mainly targeted for viewing Robot Framework debug files set
with '--debugfile' command line option when running test. The idea is to
provide a tool that has similar functionality as 'tail -f' command in 
unixy systems.

The tool has a simple GUI which is updated every time the file opened into
it is updated. File can be given from command line or opened using 'Open'
button in the GUI.
"""

import os
import sys
import time

from FileDialog import LoadFileDialog
import Tkinter as Tk


class FileViewer:
    
    def __init__(self, path=None):
        self._path = path is not None and os.path.abspath(path) or None
        self._file = self._open_file(path)
        self._root = self._create_root()
        self._create_components(self._root)
        self._last_update_cmd = None
        self._update()
        
    def mainloop(self):
        self._root.mainloop()
        
    def _create_root(self):
        root = Tk.Tk()
        root.title('Debug file viewer, v0.1')
        root.geometry('750x500+100+100')
        return root
        
    def _create_components(self, root):
        self._create_toolbar(root)
        self._create_statusbar(root)
        self._text_area = self._create_scrollable_text_area(root)

    def _create_statusbar(self, root):
        statusbar = Tk.Frame(root)
        self._statusbar_left = Tk.Label(statusbar)
        self._statusbar_left.pack(side=Tk.LEFT)
        self._statusbar_right = Tk.Label(statusbar)
        self._statusbar_right.pack(side=Tk.RIGHT)
        statusbar.pack(side=Tk.BOTTOM, fill=Tk.X)
        
    def _create_toolbar(self, root):
        toolbar = Tk.Frame(root, width=65)
        self._create_button(toolbar, 'Open', self._open_file_dialog)
        self._create_button(toolbar, 'Clear', self._clear_text)
        self._create_button(toolbar, 'Exit', self._root.destroy)
        self._pause_cont_button = self._create_button(toolbar, 'Pause', 
                                                      self._pause_or_cont, 25)
        toolbar.pack_propagate(0)
        toolbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    
    def _create_button(self, parent, label, command, pady=2):
        button = Tk.Button(parent, text=label, command=command)
        button.pack(side=Tk.TOP, padx=2, pady=pady, fill=Tk.X)
        return button

    def _create_scrollable_text_area(self, root):
        scrollbar = Tk.Scrollbar(root)
        text = Tk.Text(root, yscrollcommand=scrollbar.set, font=("Courier", 9))
        scrollbar.config(command=text.yview)
        scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
        text.pack(fill=Tk.BOTH, expand=1)
        return text
        
    def _pause_or_cont(self):
        if self._pause_cont_button['text'] == 'Pause':
            if self._last_update_cmd is not None:
                self._root.after_cancel(self._last_update_cmd)
            self._pause_cont_button.configure(text='Continue')
        else:
            self._pause_cont_button.configure(text='Pause')
            self._root.after(50, self._update)

    def _update(self):
        if self._file is None:
            self._file = self._open_file(self._path)
        if self._file is not None:
            try:
                if os.stat(self._path).st_size < self._last_file_size:
                    self._file.seek(0)
                    self._clear_text()
                self._text_area.insert(Tk.END, self._file.read())
                self._last_file_size = self._file.tell()
            except (OSError, IOError):
                self._file = None
                self._clear_text()
            self._text_area.yview('moveto', '1.0')
        self._set_status_bar_text()
        self._last_update_cmd = self._root.after(50, self._update)
        
    def _clear_text(self):
        self._text_area.delete(1.0, Tk.END)

    def _set_status_bar_text(self):
        left, right = self._path, ''
        if self._path is None:
            left = 'No file opened'
        elif self._file is None:
            right = 'File does not exist'
        else:
            timetuple = time.localtime(os.stat(self._path).st_mtime)
            timestamp = '%d%02d%02d %02d:%02d:%02d' % timetuple[:6]
            right = 'File last modified: %s' % timestamp
        self._statusbar_left.configure(text=left)
        self._statusbar_right.configure(text=right) 
        
    def _open_file(self, path):
        if path is not None and os.path.exists(path):
            self._last_file_size = os.stat(path).st_size
            return open(path)
        return None
    
    def _open_file_dialog(self):
        dialog = LoadFileDialog(self._root, title='Choose file to view')
        fname = dialog.go()
        if fname is None:
            return
        self._path = os.path.abspath(fname)
        if self._last_update_cmd is not None:
            self._root.after_cancel(self._last_update_cmd)
        if self._file is not None:
            self._file.close()
        self._file = self._open_file(self._path)
        self._clear_text()
        if self._pause_cont_button['text'] == 'Continue':
            self._pause_or_cont()
        else:
            self._update()

    
if __name__ == '__main__':
    if len(sys.argv) > 2 or '--help' in sys.argv:
        print __doc__
        sys.exit(1)
    app = FileViewer(*sys.argv[1:])
    app.mainloop()
