from javax.swing import JFrame, JList, JPanel, JLabel, JTextField, JButton, Box
from javax.swing.event import ListSelectionListener
from java.awt.event import ActionListener
from java.awt import FlowLayout, GridLayout, BorderLayout

from vacalc.employeestore import Employee


class VacalcFrame(object):

    def __init__(self, employees):
        self._frame = JFrame('Vacation Calculator',
                             defaultCloseOperation=JFrame.EXIT_ON_CLOSE)
        self._create_ui(employees)
        self._frame.pack()

    def _create_ui(self, employees):
        panel = JPanel(layout=FlowLayout())
        detais_panel = JPanel(layout=BorderLayout())
        self._employee_list = self._create_employee_list(employees)
        detais_panel.add(self._employee_list.widget, BorderLayout.PAGE_START)
        self._details = EmployeeDetailsPanel(employees)
        btn = JButton('New Employee')
        btn.addActionListener(ListenerFactory(ActionListener, self._new_employee))
        detais_panel.add(btn, BorderLayout.PAGE_END)
        panel.add(detais_panel)
        panel.add(self._details.widget)
        self._frame.setContentPane(panel)

    def _create_employee_list(self, employeestore):
        list = EmployeeList(employeestore.get_all_employees())
        list.add_selection_listener(ListenerFactory(ListSelectionListener,
                                                    self._list_item_selected))
        return list

    def _list_item_selected(self, event):
        self._details.show_employee(self._employee_list.selected_employee())

    def _new_employee(self, event):
        self._details.edit_new_employee()

    def show(self):
        self._frame.setVisible(True)


class EmployeeList(object):

    def __init__(self, employees):
        self._employees = employees
        data = [e.name for e in employees]
        self._list = JList(data, preferredSize=(200, 200))

    def add_selection_listener(self, listener):
        self._list.addListSelectionListener(listener)

    def selected_employee(self):
        return self._employees[self._list.getSelectedIndex()]

    @property
    def widget(self):
        return self._list


class EmployeeDetailsPanel(object):

    def __init__(self, employeestore):
        self._store = employeestore
        self._panel = JPanel(layout=BorderLayout(), preferredSize=(300, 200))
        itempanel = JPanel(layout=GridLayout(3,2))
        itempanel.add(JLabel(text='Name'))
        self._name_editor = JTextField()
        itempanel.add(self._name_editor)
        itempanel.add(JLabel(text='Start'))
        self._start_date_editor = JTextField()
        itempanel.add(self._start_date_editor)
        button = JButton('Save')
        button.addActionListener(ListenerFactory(ActionListener,
                                                 self._add_button_pushed))
        btnpanel = Box.createHorizontalBox()
        btnpanel.createVerticalStrut(100)
        btnpanel.add(button)
        itempanel.add(btnpanel)
        self._panel.add(itempanel, BorderLayout.PAGE_START)

    def show_employee(self, employee):
        self._name_editor.setText(employee.name)
        self._start_date_editor.setText(str(employee.startdate))

    def edit_new_employee(self):
        self._name_editor.setText('')
        self._start_date_editor.setText('')

    @property
    def widget(self):
        return self._panel

    def _add_button_pushed(self, event):
        self._store.add_employee(Employee(self._name_editor.getText(),
                                          self._start_date_editor.getText()))


def ListenerFactory(interface, func):
    from java.lang import Object
    method = list(set(dir(interface)) - set(dir(Object)))[0]
    return type('Listener', (interface,), {method: func})()
