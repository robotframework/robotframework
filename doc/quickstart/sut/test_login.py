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
        self.assertEquals(db.getvalue(),
                          'James\tSecret007\tActive\nuser\tT3stpass\tInactive\n')

    def test_invalid_password_length(self):
        msg = 'Password must be 7-12 characters long' 
        for pwd in ['Sh0rt', 'T0olongpassword', '']:
            self._verify_creating_fails_with_invalid_password(pwd, msg)    

    def test_invalid_password_content(self): 
        msg = 'Password must be a combination of lowercase and uppercase ' \
                + 'letters and numbers'
        for pwd in ['N0L0W3R', 'n0c4pses', 'NoNumbers', 'aB1/(&%#&"']:
            print pwd
            self._verify_creating_fails_with_invalid_password(pwd, msg)
           
    def _verify_creating_fails_with_invalid_password(self, pwd, msg):   
       try:
           User('testuser', pwd)
           self.fail("Creating user with password '%s' should have failed "
                     "with error message '%s' but it passed." % (pwd, msg))
       except ValueError, err:
           self.assertEquals(str(err), msg)



class TestCreateUser(unittest.TestCase):

    def setUp(self):
        self._dbfile = StringIO()
        self._db = DataBase(self._dbfile)

    def test_create_user(self):
        self._db.create_user('testu', 'P4ssw0rd') 
        self.assertEquals(self._db._users['testu'].password, 'P4ssw0rd')

class TestLogin(unittest.TestCase):

    def setUp(self):
        self._db = DataBase(StringIO('testu\tP4ssw0rd\n'))

    def test_succesful_login(self):
        self.assertEquals(self._db.login('testu', 'P4ssw0rd'), 'Logged In')

    def test_invalid_login(self):
        self.assertEquals(self._db.login('inv', 'alid'), 'Access Denied')

    def test_succesful_login_changes_status(self):
        self.assertEquals(self._db.status('testu'), 'Inactive')


if __name__ == '__main__':
	unittest.main()
