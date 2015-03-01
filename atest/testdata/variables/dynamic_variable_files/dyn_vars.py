try:
    from UserDict import UserDict
except ImportError: # Python 3
    from collections import UserDict
try:
    from collections import Mapping
except ImportError:
    Mapping = None


def get_variables(type):
    return {'dict': get_dict,
            'mydict': MyDict,
            'Mapping': get_MyMapping,
            'UserDict': get_UserDict,
            'MyUserDict': MyUserDict,
            'JavaMap': get_JavaMap}[type]()


def get_dict():
    return {'from dict': 'This From Dict', 'from dict2': 2}


class MyDict(dict):

    def __init__(self):
        dict.__init__(self, from_my_dict='This From My Dict', from_my_dict2=2)


def get_MyMapping():
    data = {'from Mapping': 'This From Mapping', 'from Mapping2': 2}
    if not Mapping:
        return data

    class MyMapping(Mapping):

        def __init__(self, data):
            self.data = data

        def __getitem__(self, item):
            return self.data[item]

        def __len__(self):
            return len(self.data)

        def __iter__(self):
            return iter(self.data)

    return MyMapping(data)


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
