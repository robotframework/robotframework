import os
import sys


class LoginLibrary:

    def __init__(self):
        sut_path = os.path.join(os.path.dirname(__file__),
                                '..', 'sut', 'login.py')
        self._command_prefix = '%s %s ' % (sys.executable, sut_path)
        self._status = ''

    def create_user(self, username='', password=''):
        command = 'create %s %s' % (username, password)
        self._run_command(command)

    def attempt_to_login_with_credentials(self, username='', password=''):
        command = 'login %s %s' % (username, password)
        self._run_command(command)

    def status_should_be(self, expected_status):
        if expected_status != self._status:
            raise AssertionError("Expected status to be '%s' but was '%s'"
                                  % (expected_status, self._status))

    def _run_command(self, command):
        command = '%s %s' % (self._command_prefix, command)
        process = os.popen(command)
        self._status = process.read().strip()
        process.close()
