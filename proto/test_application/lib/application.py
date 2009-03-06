import os
from javax.swing import JPanel, JPasswordField, JButton, JTextField, JFrame, \
    JLabel, JMenuBar, JMenu, JMenuItem, JSeparator
from java.awt import GridBagLayout, GridBagConstraints
from java.awt.event import ActionListener


VALID_USERS = [('demo', 'mode'), ('dave', 'wibble')]
STATUSFILE = os.path.join(os.path.dirname(__file__), 'store')


class MainFrame(JFrame):

    def __init__(self):
        JFrame.__init__(self, title='Login Application', size=(600, 300))
        self.setJMenuBar(MenuBar(self))
        self._login_panel = LoginPanel(self)
        self._logged_in_panel = LoggedInPanel(self)
        self.setContentPane(self._login_panel)
        self._login_if_stored()
    
    def _login_if_stored(self):
        if not os.path.isfile(STATUSFILE):
            return
        stored_user = open(STATUSFILE).read()
        if stored_user:
            self._login(stored_user)
    
    def login(self):
        username, password = self._login_panel.username, self._login_panel.password
        if (username, password) in VALID_USERS:
            self._login(username)
            self._store_logged_user(username)
        else:
            self._login_panel.set_status('Login Failed!')
        self._login_panel.reset()
        self.validate()

    def _login(self, username):
        status = 'You have logged in as "%s". Now you can logout.' % username
        self._logged_in_panel.set_status(status)
        self.setContentPane(self._logged_in_panel)

    def _store_logged_user(self, username):
        open(STATUSFILE, 'w').write(username + '\n')

    def logout(self):
        self._login_panel.set_status()
        self.setContentPane(self._login_panel)
        self._reset_store()
        self.validate()

    def _reset_store(self):
        if os.path.isfile(STATUSFILE):
            os.remove(STATUSFILE)


class MenuBar(JMenuBar):
    
    def __init__(self, parent):
        self.add(FileMenu(parent))


class FileMenu(JMenu):
    
    def __init__(self, parent):
        JMenu.__init__(self, 'File')
        self.add(MenuItem('Logout', parent.logout))
        self.add(JSeparator())
        self.add(MenuItem('Exit', parent.dispose))


class MenuItem(JMenuItem, ActionListener):
        
    def __init__(self, name, action):
        JMenuItem.__init__(self, name)
        self._action = action
        self.addActionListener(self)

    def actionPerformed(self, event):
        self._action()


class _LoginAppPanel(JPanel):

    def __init__(self, parent):
        self.layout = GridBagLayout()
        self._create_components(parent)

    def _create_button(self, label, name, listener):
        button = JButton(label=label, name=name)
        button.addActionListener(listener)
        return button

    def _add(self, component, *coords):
        """Adds component to GridBagLayout. coords are in format (col, row)"""
        constraints = GridBagConstraints()
        constraints.gridx, constraints.gridy = coords
        constraints.fill = GridBagConstraints.VERTICAL
        self.add(component, constraints)
    
    def set_status(self, message=''):
        self._status_field.text = message


class LoginPanel(_LoginAppPanel):

    username = property(lambda self: self._username_field.text)
    password = property(lambda self: self._password_field.text)

    def _create_components(self, parent):
        self._create_labels()
        self._create_input_fields()
        self._create_login_button(parent)

    def _create_labels(self):
        self._add(JLabel(text='username'), 0, 0)
        self._add(JLabel(text='password'), 0, 1)
        self._status_field = JLabel(name='status_label')
        self._add(self._status_field, 1, 2)

    def _create_input_fields(self):
        self._username_field = JTextField(20, name='username_field')
        self._add(self._username_field, 1, 0)
        self._password_field = JPasswordField(20, name='password_field')
        self._add(self._password_field, 1, 1)

    def _create_login_button(self, parent):
        self._add(self._create_button('Login', 'login_button', 
                                      SimpleAction(parent.login)), 0, 2)

    def reset(self):
        self._username_field.text = self._password_field.text = ''


class LoggedInPanel(_LoginAppPanel):

    def _create_components(self, parent):
        self._status_field = JLabel(name='status_label')
        self._add(self._status_field, 1, 1)
        self._add(self._create_button('Logout', 'logout_button', 
                                      SimpleAction(parent.logout)), 1, 2)


class SimpleAction(ActionListener):
    
    def __init__(self, action):
        """Creates a simple ActionListener. 
        
        'action' must be a callable that will be called on actionPerformed"""
        self._action = action

    def actionPerformed(self, event):
        self._action()


if __name__ == '__main__':
    MainFrame().show()

