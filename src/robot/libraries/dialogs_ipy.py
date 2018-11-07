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

import wpf    # Loads required .NET Assemblies behind the scenes

from System.Windows import (GridLength, SizeToContent, TextWrapping, Thickness,
                            Window, WindowStartupLocation)
from System.Windows.Controls import (Button, ColumnDefinition, Grid, Label, ListBox,
                                     PasswordBox, RowDefinition, TextBlock, TextBox, SelectionMode)


class _WpfDialog(Window):
    _left_button = 'OK'
    _right_button = 'Cancel'

    def __init__(self, message, value=None, **extra):
        self._initialize_dialog()
        self._create_body(message, value, **extra)
        self._create_buttons()
        self._bind_esc_to_close_dialog()
        self._result = None

    def _initialize_dialog(self):
        self.Title = 'Robot Framework'
        self.SizeToContent = SizeToContent.WidthAndHeight
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.MinWidth = 300
        self.MinHeight = 100
        self.MaxWidth = 640
        grid = Grid()
        left_column = ColumnDefinition()
        right_column = ColumnDefinition()
        grid.ColumnDefinitions.Add(left_column)
        grid.ColumnDefinitions.Add(right_column)
        label_row = RowDefinition()
        label_row.Height = GridLength.Auto
        selection_row = RowDefinition()
        selection_row.Height = GridLength.Auto
        button_row = RowDefinition()
        button_row.Height = GridLength(50)
        grid.RowDefinitions.Add(label_row)
        grid.RowDefinitions.Add(selection_row)
        grid.RowDefinitions.Add(button_row)
        self.Content = grid

    def _create_body(self, message, value, **extra):
        _label = Label()
        textblock = TextBlock()
        textblock.Text = message
        textblock.TextWrapping = TextWrapping.Wrap
        _label.Content = textblock
        _label.Margin = Thickness(10)
        _label.SetValue(Grid.ColumnSpanProperty, 2)
        _label.SetValue(Grid.RowProperty, 0)
        self.Content.AddChild(_label)
        selector = self._create_selector(value, **extra)
        if selector:
            self.Content.AddChild(selector)
            selector.Focus()

    def _create_selector(self, value):
        return None

    def _create_buttons(self):
        self.left_button = self._create_button(self._left_button,
                                               self._left_button_clicked)
        self.left_button.SetValue(Grid.ColumnProperty, 0)
        self.left_button.IsDefault = True
        self.right_button = self._create_button(self._right_button,
                                                self._right_button_clicked)
        if self.right_button:
            self.right_button.SetValue(Grid.ColumnProperty, 1)
            self.Content.AddChild(self.right_button)
            self.left_button.SetValue(Grid.ColumnProperty, 0)
            self.Content.AddChild(self.left_button)
        else:
            self.left_button.SetValue(Grid.ColumnSpanProperty, 2)
            self.Content.AddChild(self.left_button)

    def _create_button(self, content, callback):
        if content:
            button = Button()
            button.Margin = Thickness(10)
            button.MaxHeight = 50
            button.MaxWidth = 150
            button.SetValue(Grid.RowProperty, 2)
            button.Content = content
            button.Click += callback
            return button

    def _bind_esc_to_close_dialog(self):
        # There doesn't seem to be easy way to bind esc otherwise than having
        # a cancel button that binds it automatically. We don't always have
        # actual cancel button so need to create one and make it invisible.
        # Cannot actually hide it because it won't work after that so we just
        # make it so small it is not seen.
        button = Button()
        button.IsCancel = True
        button.MaxHeight = 1
        button.MaxWidth = 1
        self.Content.AddChild(button)

    def _left_button_clicked(self, sender, event_args):
        if self._validate_value():
            self._result = self._get_value()
            self._close()

    def _validate_value(self):
        return True

    def _get_value(self):
        return None

    def _close(self):
        self.Close()

    def _right_button_clicked(self, sender, event_args):
        self._result = self._get_right_button_value()
        self._close()

    def _get_right_button_value(self):
        return None

    def show(self):
        self.ShowDialog()
        return self._result


class MessageDialog(_WpfDialog):
    _right_button = None


class InputDialog(_WpfDialog):

    def __init__(self, message, default='', hidden=False):
        _WpfDialog.__init__(self, message, default, hidden=hidden)

    def _create_selector(self, default, hidden):
        if hidden:
            self._entry = PasswordBox()
            self._entry.Password = default if default else ''
        else:
            self._entry = TextBox()
            self._entry.Text = default if default else ''
        self._entry.SetValue(Grid.RowProperty, 1)
        self._entry.SetValue(Grid.ColumnSpanProperty, 2)
        self.Margin = Thickness(10)
        self._entry.Height = 30
        self._entry.Width = 150
        self._entry.SelectAll()
        return self._entry

    def _get_value(self):
        try:
            return self._entry.Text
        except AttributeError:
            return self._entry.Password


class SelectionDialog(_WpfDialog):

    def __init__(self, message, values):
        _WpfDialog.__init__(self, message, values)

    def _create_selector(self, values):
        self._listbox = ListBox()
        self._listbox.SetValue(Grid.RowProperty, 1)
        self._listbox.SetValue(Grid.ColumnSpanProperty, 2)
        self._listbox.Margin = Thickness(10)
        for item in values:
            self._listbox.Items.Add(item)
        return self._listbox

    def _validate_value(self):
        return bool(self._listbox.SelectedItem)

    def _get_value(self):
        return self._listbox.SelectedItem


class MultipleSelectionDialog(_WpfDialog):

    def __init__(self, message, values):
        _WpfDialog.__init__(self, message, values)

    def _create_selector(self, values):
        self._listbox = ListBox()
        self._listbox.SelectionMode = SelectionMode.Multiple
        self._listbox.SetValue(Grid.RowProperty, 1)
        self._listbox.SetValue(Grid.ColumnSpanProperty, 2)
        self._listbox.Margin = Thickness(10)
        for item in values:
            self._listbox.Items.Add(item)
        return self._listbox

    def _get_value(self):
        return sorted(self._listbox.SelectedItems,
                      key=list(self._listbox.Items).index)


class PassFailDialog(_WpfDialog):
    _left_button = 'PASS'
    _right_button = 'FAIL'

    def _get_value(self):
        return True

    def _get_right_button_value(self):
        return False
