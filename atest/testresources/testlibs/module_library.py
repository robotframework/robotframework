ROBOT_LIBRARY_SCOPE = 'Test Suite'  # this should be ignored
__version__ = 'test'  # this should be used as version of this library


def passing():
    pass

def failing():
    raise AssertionError('This is a failing keyword from module library')

def logging():
    print('Hello from module library')
    print('*WARN* WARNING!')

def returning():
    return 'Hello from module library'

def argument(arg):
    assert arg == 'Hello', "Expected 'Hello', got '%s'" % arg

def many_arguments(arg1, arg2, arg3):
    assert arg1 == arg2 == arg3, ("All arguments should have been equal, got: "
                                  "%s, %s and %s") % (arg1, arg2, arg3)

def default_arguments(arg1, arg2='Hi', arg3='Hello'):
    many_arguments(arg1, arg2, arg3)

def variable_arguments(*args):
    return sum([int(arg) for arg in args])

attribute = 'This is not a keyword!'

class NotLibrary:

    def two_arguments(self, arg1, arg2):
        msg = "Arguments should have been unequal, both were '%s'" % arg1
        assert arg1 != arg2, msg

    def not_keyword(self):
        pass


notlib = NotLibrary()
two_arguments_from_class = notlib.two_arguments

lambda_keyword = lambda arg: int(arg) + 1
lambda_keyword_with_two_args = lambda x, y: int(x) / int(y)

def _not_keyword():
    pass

def module_library():
    return "It should be OK to have an attribute with same name as the module"

