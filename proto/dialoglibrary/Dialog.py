'''Dialogs is a test library that provides means for pausing the test execution
and asking user input'''


def pause_execution(message='Press OK to continue.'):
    """Pauses the test execution and shows dialog with text `message`.
    """
    _pause_execution(message)

def execute_manual_step(message='Set keyword status', error='Execution failed'):
    """Pauses the test execution and shows a dialog with text `message`.

    User can choose to pass or fail the test. In case of failing the test,
    additional dialog is opened for defining the error message.
    """
    _execute_manual_step(message, error)

def get_value_from_user(message='Give value:', default=''):
    """Pauses the test execution and asks user to input value.

    `message` is the instruction to user. `default` is the default value of the
    input field.
    """
    return _get_value_from_user(message, default)


import sys

if sys.platform.startswith('java'):

    from javax.swing.JOptionPane import showMessageDialog, showOptionDialog,\
        showInputDialog, YES_NO_OPTION, PLAIN_MESSAGE


    def _pause_execution(message):
        showMessageDialog(None, message, 'Paused', PLAIN_MESSAGE)

    def _execute_manual_step(message, error):
        status = showOptionDialog(None, message, 'Paused', YES_NO_OPTION,
                                  PLAIN_MESSAGE, None, ['PASS', 'FAIL'], None)
        if status != 0:
            msg = _get_value_from_user('Give error message:', 'Failed') 
            raise AssertionError(msg)

    def _get_value_from_user(message, default):
        value = showInputDialog(None, message, 'Paused', PLAIN_MESSAGE,
                                None, None, default)
        if value is None:
            raise ValueError('No value provided by user')    
        return value


else:

    from Tkinter import Tk, Label 
    import tkMessageBox
    import tkSimpleDialog


    def _pause_execution(message):
        Tk().withdraw() # Hides the main frame.
        tkMessageBox.showinfo('Paused', message)

    def _execute_manual_step(message, error):
        Tk().withdraw() # Hides the main frame.
        if not tkMessageBox.askyesno('Paused', message + '\n\nYes means PASS, No means FAIL'):
            msg = _get_value_from_user('Give error message:', 'Failed')
            raise AssertionError(msg)

    def _get_value_from_user(message, default):
        value = tkSimpleDialog.askstring('Paused', message, initialvalue=default)
        if value is None:
            raise ValueError('No value provided by user')    
        return value

