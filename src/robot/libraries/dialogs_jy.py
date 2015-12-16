#  Copyright 2008-2015 Nokia Solutions and Networks
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

from java.awt import GridLayout
from java.awt.event import WindowAdapter
from javax.swing import JLabel, JOptionPane, JPanel, JPasswordField, JTextField
from javax.swing.JOptionPane import (DEFAULT_OPTION, OK_CANCEL_OPTION,
                                     OK_OPTION, PLAIN_MESSAGE,
                                     UNINITIALIZED_VALUE, YES_NO_OPTION)


class _SwingDialog(object):

    def __init__(self, pane):
        self._pane = pane

    def show(self):
        self._show_dialog(self._pane)
        return self._get_value(self._pane)

    def _show_dialog(self, pane):
        dialog = pane.createDialog(None, 'Robot Framework')
        dialog.setModal(False)
        dialog.setAlwaysOnTop(True)
        dialog.addWindowFocusListener(pane.focus_listener)
        dialog.show()
        while dialog.isShowing():
            time.sleep(0.2)
        dialog.dispose()

    def _get_value(self, pane):
        value = pane.getInputValue()
        return value if value != UNINITIALIZED_VALUE else None


class MessageDialog(_SwingDialog):

    def __init__(self, message):
        pane = WrappedOptionPane(message, PLAIN_MESSAGE, DEFAULT_OPTION)
        _SwingDialog.__init__(self, pane)


class InputDialog(_SwingDialog):

    def __init__(self, message, default, hidden=False):
        self._input_field = JPasswordField() if hidden else JTextField()
        self._input_field.setText(default)
        self._input_field.selectAll()
        panel = JPanel(layout=GridLayout(2, 1))
        panel.add(JLabel(message))
        panel.add(self._input_field)
        pane = WrappedOptionPane(panel, PLAIN_MESSAGE, OK_CANCEL_OPTION)
        pane.set_focus_listener(self._input_field)
        _SwingDialog.__init__(self, pane)

    def _get_value(self, pane):
        if pane.getValue() != OK_OPTION:
            return None
        return self._input_field.getText()


class SelectionDialog(_SwingDialog):

    def __init__(self, message, options):
        pane = WrappedOptionPane(message, PLAIN_MESSAGE, OK_CANCEL_OPTION)
        pane.setWantsInput(True)
        pane.setSelectionValues(options)
        _SwingDialog.__init__(self, pane)


class PassFailDialog(_SwingDialog):

    def __init__(self, message):
        pane = WrappedOptionPane(message, PLAIN_MESSAGE, YES_NO_OPTION,
                                 None, ['PASS', 'FAIL'], 'PASS')
        _SwingDialog.__init__(self, pane)

    def _get_value(self, pane):
        value = pane.getValue()
        return value == 'PASS' if value in ['PASS', 'FAIL'] else None


class WrappedOptionPane(JOptionPane):
    focus_listener = None

    def getMaxCharactersPerLineCount(self):
        return 120

    def set_focus_listener(self, component):
        self.focus_listener = WindowFocusListener(component)


class WindowFocusListener(WindowAdapter):

    def __init__(self, component):
        self.component = component

    def windowGainedFocus(self, event):
        self.component.requestFocusInWindow()
