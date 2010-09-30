from javax.swing import JFrame, JList, JPanel, JLabel, JTextField, JButton, Box, BoxLayout, JTable
from javax.swing.event import ListSelectionListener
from javax.swing.table import AbstractTableModel
from java.awt.event import ActionListener
from java.awt import FlowLayout, BorderLayout, Dimension, Font, Color


class VacalcFrame(object):

    def __init__(self, employees):
        self._frame = JFrame('Vacation Calculator',
                             defaultCloseOperation=JFrame.EXIT_ON_CLOSE)
        self._frame.setContentPane(self._create_ui(employees))
        self._frame.pack()

    def _create_ui(self, employees):
        panel = JPanel(layout=FlowLayout())
        self._overview = EmployeeOverview(employees, self)
        self._details = EmployeeDetails(employees)
        panel.add(self._overview)
        panel.add(self._details)
        return panel

    def show(self):
        self._frame.setVisible(True)

    def employees_changed(self):
        self._overview.refresh()

    def employee_selected(self, employee):
        self._details.show_employee(employee)

    def edit_new_employee(self):
        self._details.edit_new_employee()


class EmployeeOverview(JPanel):

    def __init__(self, employees, overview_listener):
        JPanel.__init__(self, layout=BorderLayout())
        self._listener = overview_listener
        self._employee_list = self._create_employee_list(employees)
        new_emp_btn = self._create_new_employee_button()
        self.add(self._employee_list.widget, BorderLayout.PAGE_START)
        self.add(new_emp_btn, BorderLayout.PAGE_END)

    def _create_employee_list(self, employees):
        list = EmployeeList(employees)
        list.add_selection_listener(ListenerFactory(ListSelectionListener,
                                                    self._list_item_selected))
        return list

    def _create_new_employee_button(self):
        btn = JButton('New Employee', name='new_employee_button')
        btn.addActionListener(ListenerFactory(ActionListener, self._new_employee))
        return btn

    def _list_item_selected(self, event):
        self._listener.employee_selected(self._employee_list.selected_employee())

    def _new_employee(self, event):
        self._employee_list.clear_selection()
        self._listener.edit_new_employee()

    def refresh(self):
        self._employee_list.refresh()


class EmployeeList(object):

    def __init__(self, employees):
        self._employees = employees
        self._employees.add_change_listener(self)
        self._list = JList(preferredSize=(200, 200), name='employee_list')
        self._populate_list()

    def _populate_list(self):
        self._list.setListData([e.name for e in self._employees.all()])

    def add_selection_listener(self, listener):
        self._list.addListSelectionListener(listener)

    def selected_employee(self):
        return self._employees.all()[self._list.getSelectedIndex()]

    def employee_added(self, employee):
        self._populate_list()
        self._list.setSelectedValue(employee.name, True)

    def adding_employee_failed(self, error):
        pass

    def clear_selection(self):
        self._list.clearSelection()

    def refresh(self):
        idx = self._list.getSelectedIndex()
        self._populate_list()
        if idx < self._list.getModel().getSize():
            self._list.setSelectedIndex(idx)

    @property
    def widget(self):
        return self._list


class EmployeeDetails(JPanel):

    def __init__(self, employees):
        JPanel.__init__(self, preferredSize=(300, 200))
        layout = BoxLayout(self, BoxLayout.Y_AXIS)
        self.setLayout(layout)
        self._employees = employees
        employees.add_change_listener(self)
        self._create_status_label()
        self._create_name_editor()
        self._create_start_date_editor()
        self._create_save_button()
        self._create_vacation_display()

    def _create_status_label(self):
        self._status_label = JLabel(name='status_label',
                                   font=Font(Font.SERIF, Font.PLAIN, 9))
        self.add(self._status_label)
        self._add_with_padding(self._status_label, 5)

    def _create_name_editor(self):
        self.add(JLabel(text='Name'))
        self._name_editor = FixedHeightTextField('name_input')
        self._add_with_padding(self._name_editor, 5)

    def _create_start_date_editor(self):
        self.add(JLabel(text='Start Date (YYYY-MM-DD)'))
        self._start_date_editor = FixedHeightTextField('start_input')
        self._add_with_padding(self._start_date_editor, 5)

    def _create_save_button(self):
        self._save_button = JButton('Save', name='save_button', visible=False)
        self._save_button.addActionListener(ListenerFactory(ActionListener,
                                            self._save_button_pushed))
        self._add_with_padding(self._save_button, 5)

    def _create_vacation_display(self):
        self._display = VacationTable()
        self._header = self._display.getTableHeader()
        self.add(self._header)
        self.add(self._display)

    def _add_with_padding(self, component, padding):
        self.add(component)
        self.add(Box.createRigidArea(Dimension(0, padding)))

    def show_employee(self, employee):
        self._name_editor.setText(employee.name)
        self._start_date_editor.setText(str(employee.startdate))
        self._save_button.setVisible(False)
        self._display.setVisible(True)
        self._display.setModel(VacationTableModel(employee))
        self._header.setVisible(True)

    def edit_new_employee(self):
        self._name_editor.setText('')
        self._start_date_editor.setText('')
        self._save_button.setVisible(True)
        self._display.setVisible(False)
        self._header.setVisible(False)

    def _save_button_pushed(self, event):
        self._employees.add(self._name_editor.getText(),
                            self._start_date_editor.getText())

    def employee_added(self, employee):
        self._status_label.setForeground(Color.BLACK)
        self._status_label.setText("Employee '%s' was added successfully." % employee.name)
        self._save_button.setVisible(False)

    def adding_employee_failed(self, reason):
        self._status_label.setForeground(Color.RED)
        self._status_label.setText(reason)


class FixedHeightTextField(JTextField):

    def __init__(self, name):
        JTextField.__init__(self, name=name)
        prefsize = self.preferredSize
        maxsize = self.maximumSize
        self.setMaximumSize(Dimension(maxsize.width, prefsize.height))


class VacationTableModel(AbstractTableModel):
    _columns = ['Year', 'Vacation']

    def __init__(self, employee):
        self._employee = employee

    def getColumnName(self, index):
        return self._columns[index]

    def getColumnCount(self):
        return 2

    def getRowCount(self):
        return 1

    def getValueAt(self, row, col):
        if col == 0:
            return '2010'
        return self._employee.count_vacation(2010)


class VacationTable(JTable):

    def __init__(self):
        JTable.__init__(self)


def ListenerFactory(interface, func):
    from java.lang import Object
    method = list(set(dir(interface)) - set(dir(Object)))[0]
    return type('Listener', (interface,), {method: func})()
