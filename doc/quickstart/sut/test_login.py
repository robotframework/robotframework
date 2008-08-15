import unittest
from StringIO import StringIO

from login import DataBase, User


class TestUser(unittest.TestCase):

    def test_initialization(self):
        u = User('name', 'pw')
        self.assertEquals(u.username, 'name')
        self.assertEquals(u.password, 'pw')
        self.assertEquals(u.status, 'Inactive')

    def test_init_with_status(self):
        u = User('James', '007', 'Active')
        self.assertEquals(u.username, 'James')
        self.assertEquals(u.password, '007')
        self.assertEquals(u.status, 'Active')
        
    def test_serialize(self):
        db = StringIO()
        User('James', '007', 'Active').serialize(db)
        self.assertEquals(db.getvalue(), 'James\t007\tActive\n')
        User('user', 'pass').serialize(db)
        self.assertEquals(db.getvalue(),
                          'James\t007\tActive\nuser\tpass\tInactive\n')


class TestCreateUser(unittest.TestCase):

    def setUp(self):
        self._dbfile = StringIO()
        self._db = DataBase(self._dbfile)

    def test_create_user(self):
        self._db.create_user('testu', 'testpw') 
        self.assertEquals(self._db._users['testu'].password, 'testpw')


class TestLogin(unittest.TestCase):

    def setUp(self):
        self._db = DataBase(StringIO('testu\ttestpw\n'))

    def test_succesful_login(self):
        self.assertEquals(self._db.login('testu', 'testpw'), 'Logged In')

    def test_invalid_login(self):
        self.assertEquals(self._db.login('inv', 'alid'), 'Access Denied')

    def test_succesful_login_changes_status(self):
        self.assertEquals(self._db.status('testu'), 'Inactive')


if __name__ == '__main__':
	unittest.main()
