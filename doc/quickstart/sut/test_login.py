import unittest
from StringIO import StringIO

from login import DataBase, User


class TestUser(unittest.TestCase):

    def test_initialization(self):
        u = User('name', 'P4ssw0rd')
        self.assertEquals(u.username, 'name')
        self.assertEquals(u.password, 'P4ssw0rd')
        self.assertEquals(u.status, 'Inactive')

    def test_init_with_status(self):
        u = User('James', 'Secret007', 'Active')
        self.assertEquals(u.username, 'James')
        self.assertEquals(u.password, 'Secret007')
        self.assertEquals(u.status, 'Active')
        
    def test_serialize(self):
        db = StringIO()
        User('James', 'Secret007', 'Active').serialize(db)
        self.assertEquals(db.getvalue(), 'James\tSecret007\tActive\n')
        User('user', 'T3stpass').serialize(db)
        self.assertEquals(db.getvalue(), 'James\tSecret007\tActive\n'
                                         'user\tT3stpass\tInactive\n')

    def test_invalid_password_length(self):
        msg = 'Password must be 7-12 characters long' 
        for pwd in ['Sh0rt', 'T0olongpassword', '']:
            self._verify_creating_fails_with_invalid_password(pwd, msg)    

    def test_invalid_password_content(self): 
        msg = 'Password must be a combination of lowercase and uppercase ' \
                + 'letters and numbers'
        for pwd in ['N0L0W3R', 'n0c4pses', 'NoNumbers', 'aB1/(&%#&"']:
            self._verify_creating_fails_with_invalid_password(pwd, msg)
           
    def _verify_creating_fails_with_invalid_password(self, pwd, msg):   
       try:
           User('testuser', pwd)
           self.fail("Creating user with password '%s' should have failed "
                     "with error message '%s' but it passed." % (pwd, msg))
       except ValueError, err:
           self.assertEquals(str(err), msg)


class TestDataBase(unittest.TestCase):

    def setUp(self):
        self._db = DataBase(StringIO('testu\tP4ssw0rd\n'))

    def test_create_user(self):
        self._db.create_user('username', 'Mypass1234') 
        self.assertEquals(self._db._users['username'].password, 'Mypass1234')

    def test_succesful_login(self):
        self.assertEquals(self._db.login('testu', 'P4ssw0rd'), 'Logged In')
        self.assertEquals(self._db._users['testu'].status, 'Active')

    def test_invalid_login(self):
        self.assertEquals(self._db.login('inv', 'alid'), 'Access Denied')
        self.assertEquals(self._db._users['testu'].status, 'Inactive')

    def test_change_password_succesfully(self):
        result = self._db.change_password('testu', 'P4ssw0rd', 'dr0wss4P') 
        self.assertEquals(result, 'SUCCESS')
        self.assertEquals(self._db._users['testu'].password, 'dr0wss4P')
       
    def test_change_password_when_user_does_not_exist(self):
        result = self._db.change_password('nonexisting', 'P4ssw0r', 'r0wss4P')
        self.assertEquals(result, 'Changing password failed: Access Denied')

    def test_change_password_with_wrong_old_password(self):
        result = self._db.change_password('testu', 'wrong', 'r0wss4P')
        self.assertEquals(result, 'Changing password failed: Access Denied')

    def test_change_password_with_invalid_new_password(self):
        result = self._db.change_password('testu', 'P4ssw0rd', 'short')
        self.assertEquals(result, 'Changing password failed: Password must '
                                  'be 7-12 characters long')
        result = self._db.change_password('testu', 'P4ssw0rd', 'invalid')
        self.assertEquals(result, 'Changing password failed: Password must be '
                                  'a combination of lowercase and uppercase ' 
                                  'letters and numbers')


if __name__ == '__main__':
	unittest.main()

