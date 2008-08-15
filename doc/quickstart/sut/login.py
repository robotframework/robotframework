import sys
import os
import tempfile

DATABASE_FILE = os.path.join(tempfile.gettempdir(), 'robot-quickstart-db.txt')


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
        user = User(username, password)
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
        self.username = username
        self.password = password
        self.status = status

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
