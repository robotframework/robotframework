from UserDict import UserDict


def get_variables(type):
    return {'dict': get_dict,
            'mydict': MyDict,
            'UserDict': get_UserDict,
            'MyUserDict': MyUserDict,
            'JavaMap': get_JavaMap}[type]()


def get_dict():
    return {'from dict': 'This From Dict', 'from dict2': 2}


class MyDict(dict):

    def __init__(self):
        dict.__init__(self, from_my_dict='This From My Dict', from_my_dict2=2)

def get_UserDict():
    return UserDict({'from UserDict': 'This From UserDict', 'from UserDict2': 2})


class MyUserDict(UserDict):

    def __init__(self):
        UserDict.__init__(self, {'from MyUserDict': 'This From MyUserDict',
                                 'from MyUserDict2': 2})


def get_JavaMap():
    from java.util import HashMap
    map = HashMap()
    map.put('from Java Map', 'This From Java Map')
    map.put('from Java Map2', 2)
    return map
