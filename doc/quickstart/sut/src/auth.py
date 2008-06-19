import os
import re
import sys

class PasswordFile:

    def __init__(self, passwords_file=None):
        self.path = passwords_file
  
    def get_users(self):
        user_accounts = {}
        data = self._get_data()
        if data is not None:
            for line in data.splitlines():
                entry = line.split("\t")
                user_accounts[entry[0]] = {'name':entry[0], 'pwd':entry[1], 
                                          'status':entry[2]}
        else:
            print Messages().lookup('load_failed')
        return user_accounts
  
    def _get_data(self):
        if self.path is None:
            return None
        if not os.path.exists(self.path):
            return ''
        password_file = open(self.path)
        data = password_file.read()
        password_file.close()
        return data        
        
    def save(self, user_accounts):
        data = ''
        for userid, values in user_accounts.items():
            data += userid + "\t" + values['pwd'] + "\t" + values['status'] + '\n'
        self._save_data(data)

    def _save_data(self, data):
        password_file = open(self.path, "w")
        password_file.write(data)
        password_file.close()

class Authentication:
  
    def __init__(self, pwd_file):
        self.pwd_file = pwd_file
        self.user_accounts = pwd_file.get_users()
  
    def account_exists(self, username):
        return self.user_accounts.has_key(username)
  
    def create(self, username, password, status='active'):
        account_data = {}
        account_data['pwd'] = password
        account_data['status'] = status
        self.user_accounts[username] = account_data
        self.pwd_file.save(self.user_accounts)
        return 'success'
  
    def login(self, username, password):
        if self.user_accounts.has_key(username) and self.user_accounts[username]['pwd'] == password:
            self.user_accounts[username]['status'] = 'online'
            self.pwd_file.save(self.user_accounts)
            return 'logged_in'
        else:
            return 'access_denied'
  
    def get_user(self, name):
        return User(name, self.user_accounts[name])

class User:
  
    def __init__(self, name, user_data):
        self.name = name
        self.pwd = user_data['pwd']
        self.status = user_data['status']
  
    def logged_in(self):
        return self.status == 'online'
  
    def password_equals(self, password):
        return password == self.pwd

class Password:

    def __init__(self, password):
        self.password = password
  
    def valid(self):
        return not self.too_short() and not self.too_long() and self.contains_punctuation() \
           and self.contains_letter() and self.contains_number()
  
    def too_short(self):
        return (len(self.password) < 6)
  
    def too_long(self):
        return (len(self.password) > 12)
  
    def contains_punctuation(self):
        return re.search('\W', self.password) is not None
  
    def contains_letter(self):
        return re.search('[a-zA-Z]', self.password) is not None
  
    def contains_number(self):
        return re.search('\d', self.password) is not None

class Messages:
    mappings = {'success':"SUCCESS",
                'fail':"FAIL",
                'unknown':"Auth Server: unknown command",
                'no_cmd':"Must provide at least one command",
                'logged_in':"Logged In",
                'load_failed':"Failed to load user accounts",
                'access_denied':"Access Denied"
               }
  
    def lookup(self, msg_symbol):
        return self.mappings[msg_symbol]

class CommandLine:
  
    def called_with(self, auth, args):
        if len(args) == 0:
            return Messages().lookup('no_cmd')
        if args[0] in dir(auth):
            return_code = getattr(auth, args[0])(args[1], args[2])
            return Messages().lookup(return_code)
        else:
            return Messages().lookup('unknown') + " '" + args[0] + "'"

# if being called from the cmd line with args
if __name__ == '__main__':
    if len(sys.argv) > 1:

        # setup the authentication server
        pwd_file = PasswordFile(os.path.join(os.path.dirname(__file__), 
                                             'pwds.txt'))
        auth = Authentication(pwd_file)

        # grab the input and write out the output to stdout
        print CommandLine().called_with(auth, sys.argv[1:])
