import os

class LoginLibrary:

    def __init__(self):
        sut_path = os.path.join(os.path.dirname(__file__),
                                '..', 'sut', 'src', 'auth.py')
        self.cmd = 'python %s' % sut_path
        self.status = ''

    def create_user(self, username="", password=""):
        command_string = '%s create %s %s' % (self.cmd, username, password)
        self.status = os.popen(command_string).read()

    def attempt_to_login_with_credentials(self, username="", password=""):
        command_string = '%s login %s %s' % (self.cmd, username, password)
        self.status = os.popen(command_string).read()

    def status_should_be(self, expected_status):
        if expected_status != self.status.strip():
            raise AssertionError("Expected status to be '%s' but was '%s'"
                                  % (expected_status, self.status))
