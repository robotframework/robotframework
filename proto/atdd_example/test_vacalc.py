import datetime
import unittest

from vacalc import User, UserStore, DuplicateUser


class TestUser(unittest.TestCase):

    def test_creating_user(self):
        user = User('Juan von Rantanen', '2010-3-15')
        self.assertEquals(user.name, 'Juan von Rantanen')
        self.assertEquals(user.startdate, datetime.date(2010, 3, 15))


class TestUserStore(unittest.TestCase):

    def test_adding_user(self):
        store = UserStore()
        user = store.add_user('Test User Store', '2000-12-24')
        self.assertEquals(user.name, 'Test User Store')
        self.assertEquals(user.startdate, datetime.date(2000, 12, 24))
        self.assertEquals(store._users, {user.name: user})

    def test_adding_duplicate_user(self):
        store = UserStore()
        user = store.add_user('test', '2000-12-24')
        self.assertRaises(DuplicateUser, store.add_user, 'test', '2001-01-24')


if __name__ == '__main__':
    unittest.main()
