import os
import sys
import StringIO
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from auth import *


class TestPassword(unittest.TestCase):

    def test_validate_password_returns_true_when_all_conventions_met(self):
        password = Password("a0!aaa")
        self.assertTrue(password.valid())
  
    def test_validate_password_returns_false_when_password_less_than_6_chars(self):
        password = Password("a0!aa")
        self.assertFalse(password.valid())

    def test_validate_password_returns_false_when_password_too_long(self):
        password = Password("a0!aaaaaaaaaa")
        self.assertFalse(password.valid())

    def test_validate_password_returns_false_when_password_missing_punctuation(self):
        password = Password("aaaaa0")
        self.assertFalse(password.valid())

    def test_validate_password_returns_false_when_password_missing_letter(self):
        password = Password("!!!!00")
        self.assertFalse(password.valid())

    def test_validate_password_returns_false_when_password_missing_number(self):
        password = Password("!!!!!A")
        self.assertFalse(password.valid())


class MockPasswordFile(PasswordFile):
    
    def __init__(self, data):
        self._save_data(data)
        
    def _get_data(self):
        return self.io.getvalue()
    
    def _save_data(self, data):
        self.io = StringIO.StringIO()
        self.io.write(data)


class TestAuth(unittest.TestCase): 

    def setUp(self):
        # using mocks to avoid polluting real pwds file with test data
        pwd_file = MockPasswordFile('')
        self.auth = Authentication(pwd_file)
  
    def test_valid_user_can_log_in(self):
        self.auth.create("sam", "a0!aaa")
        return_code = self.auth.login("sam", "a0!aaa")
        assert self.auth.get_user("sam").logged_in(), "Expected user should be logged in"
        self.assertEqual('logged_in', return_code)

    def test_auth_return_code_is_access_denied_if_login_fails(self):
        return_code = self.auth.login("aasdjfj", "")
        self.assertEqual('access_denied', return_code)

    def test_account_exists_returns_true_if_account_exists_with_username(self):
        self.auth.create("fred", "f0!ble")
        assert self.auth.account_exists("fred")

    def test_account_exists_returns_false_if_no_account_with_username(self):
        assert not self.auth.account_exists("foo")

    def test_create_user_adds_new_user_to_list_with_user_data_and_returns_success(self):
        assert not self.auth.account_exists("newacc")
        return_code = self.auth.create("newacc", "d3f!lt")
        assert self.auth.account_exists("newacc")
        self.assertEqual('success', return_code)


class TestCmd(unittest.TestCase):

    def setUp(self):
        pwd_file = MockPasswordFile('')
        self.auth = Authentication(pwd_file)

    def test_command_sent_to_auth_object(self):
        return_code = CommandLine().called_with(self.auth, ["create", "foo", "bar"])
        self.assertEqual('SUCCESS', return_code)

    def test_undefined_command_returns_error_message(self):
        return_code = CommandLine().called_with(self.auth, ["nosuchcommand"])
        self.assertEqual("Auth Server: unknown command 'nosuchcommand'", return_code)


class TestErrs(unittest.TestCase):

    def test_can_retrieve_messages(self):
        self.assertEqual("SUCCESS", Messages().lookup('success'))


if __name__ == "__main__":
    unittest.main()
