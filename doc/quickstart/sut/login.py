import sys
import os
import tempfile

DATABASE_FILE = os.path.join(tempfile.gettempdir(), 'robotframework-quickstart-db.txt')


class DataBase(object):
   
    def __init__(self, dbfile):
        """
        """
        self._dbfile, self._users = self._read_users(dbfile)

    def _read_users(self, dbfile):
        users = {}
        if isinstance(dbfile, basestring):
            if not os.path.isfile(dbfile):
                return open(dbfile, 'w'), users
            else:
                dbfile = open(dbfile, 'r+')
        for row in dbfile.read().splitlines():
            user = User(*row.split('\t'))
            users[user.username] = user
        return dbfile, users

    def create_user(self, username, password):
        try:
            user = User(username, password)
        except ValueError, err:
            return 'Creating user failed: %s' % err
        self._users[user.username] = user
        return 'SUCCESS'

    def login(self, username, password):
        if username in self._users and \
                self._users[username].password == password:
            return 'Logged In'
        return 'Access Denied'

    def status(self, username):
        return 'Inactive'

    def close(self):
        self._dbfile.truncate(0)
        for user in self._users.values():
            user.serialize(self._dbfile)
        self._dbfile.close()


class User(object):

    def __init__(self, username, password, status='Inactive'):
        self._validate_password(password)
        self.username = username
        self.password = password
        self.status = status

    def _validate_password(self, password):
        if not (6 < len(password) < 13):
            raise ValueError('Password must be 7-12 characters long')
        has_lower = has_upper = has_number = has_invalid = False
        for char in password:
            if char.islower():
                has_lower = True
            elif char.isupper():
                has_upper = True
            elif char.isdigit():
                has_number = True
            else: 
                has_invalid = True
                break
        if has_invalid or not (has_lower and has_upper and has_number):
            raise ValueError('Password must be a combination of lowercase ' 
                             'and uppercase letters and numbers')

    def serialize(self, dbfile):
        dbfile.write('%s\t%s\t%s\n' % 
                        (self.username, self.password, self.status))


def login(username, password):
    db = DataBase(DATABASE_FILE)
    print db.login(username, password)
    db.close()

def create_user(username, password):
    db = DataBase(DATABASE_FILE)
    print db.create_user(username, password)
    db.close()

def help():
    print 'Usage: %s { create | login | help } [username password]' \
             % os.path.basename(sys.argv[0])


if __name__ == '__main__':
    actions = {'create': create_user, 'login': login, 'help': help}
    try:
        action = sys.argv[1]
    except IndexError:
        action = 'help'
    args = sys.argv[2:]
    try:
        actions[action](*args)
    except (KeyError, TypeError):
        help()
