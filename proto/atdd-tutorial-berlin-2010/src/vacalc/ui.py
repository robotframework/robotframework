from javax.swing import JFrame, JList, JPanel, JLabel, JTextField, JButton, Box, JTextArea
from javax.swing.event import ListSelectionListener
from java.awt.event import ActionListener
from java.awt import FlowLayout, GridLayout, BorderLayout


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

    def _create_employee_list(self, employees):
        list = EmployeeList(employees)
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

    @property
    def widget(self):
        return self._list


class EmployeeDetailsPanel(object):

    def __init__(self, employees):
        self._employees = employees
        employees.add_change_listener(self)
        self._panel = JPanel(layout=BorderLayout(), preferredSize=(300, 200))
        itempanel = JPanel(layout=GridLayout(4,2))
        itempanel.add(JLabel(text='Name'))
        self._name_editor = JTextField(name='name_input')
        itempanel.add(self._name_editor)
        itempanel.add(JLabel(text='Start'))
        self._start_date_editor = JTextField(name='start_input')
        itempanel.add(self._start_date_editor)
        button = JButton('Save', name='save_button')
        button.addActionListener(ListenerFactory(ActionListener,
                                                 self._save_button_pushed))
        itempanel.add(Box.createHorizontalStrut(1))
        btnpanel = Box.createHorizontalBox()
        btnpanel.add(btnpanel.createHorizontalStrut(80))
        btnpanel.add(button)
        itempanel.add(btnpanel)
        self._panel.add(itempanel, BorderLayout.PAGE_START)
        self._status_label = JTextArea(editable=False, name='status_label', visible=False)
        self._panel.add(self._status_label, BorderLayout.PAGE_END)

    def show_employee(self, employee):
        self._name_editor.setText(employee.name)
        self._start_date_editor.setText(str(employee.startdate))

    def edit_new_employee(self):
        self._name_editor.setText('')
        self._start_date_editor.setText('')

    @property
    def widget(self):
        return self._panel

    def _save_button_pushed(self, event):
        self._employees.add(self._name_editor.getText(),
                            self._start_date_editor.getText())

    def employee_added(self, employee):
        self._status_label.setText("Employee '%s' was added successfully" % employee.name)

    def adding_employee_failed(self, reason):
        self._status_label.setText(reason)
        self._status_label.setVisible(True)


def ListenerFactory(interface, func):
    from java.lang import Object
    method = list(set(dir(interface)) - set(dir(Object)))[0]
    return type('Listener', (interface,), {method: func})()
