try:
    from UserDict import UserDict
except ImportError: # Python 3
    from collections import UserDict

def get_variables(type):
    return {'dict': get_dict,
            'mydict': MyDict,
            'UserDict': get_UserDict,
            'MyUserDict': get_MyUserDict,
            'JavaMap': get_JavaMap}[type]()


def get_dict():
    return {'from dict': 'This From Dict', 'from dict2': 2}

class MyDict(dict):
    def __init__(self):
        dict.__init__(self, from_my_dict='This From My Dict', from_my_dict2=2)

def get_UserDict():
    userdict = UserDict()
    userdict.update({'from UserDict': 'This From UserDict', 'from UserDict2': 2})
    return userdict

class MyUserDict(UserDict):
    def __init__(self, dict):
        self.data = {}
        self.update(dict)

def get_MyUserDict(*args):
    return MyUserDict({'from MyUserDict': 'This From MyUserDict', 
                       'from MyUserDict2': 2})

def get_JavaMap():
    from java.util import HashMap
    map = HashMap()
    map.put('from Java Map', 'This From Java Map')
    map.put('from Java Map2', 2)
    return map
