import os
import sys
import subprocess


class LoginLibrary:

    def __init__(self):
        self._sut_path = os.path.join(os.path.dirname(__file__),
                                      '..', 'sut', 'login.py')
        self._status = ''

    def create_user(self, username, password):
        self._run_command('create', username, password)

    def change_password(self, username, old_pwd, new_pwd):
        self._run_command('change-password', username, old_pwd, new_pwd)

    def attempt_to_login_with_credentials(self, username, password):
        self._run_command('login', username, password)

    def status_should_be(self, expected_status):
        if expected_status != self._status:
            raise AssertionError("Expected status to be '%s' but was '%s'"
                                  % (expected_status, self._status))

    def _run_command(self, command, *args):
        if not sys.executable:
            raise RuntimeError("Could not find Jython installation")
        command = [sys.executable, self._sut_path, command] + list(args)
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        self._status = process.communicate()[0].strip()
