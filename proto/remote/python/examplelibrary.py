import os.path
import sys
import types


class PythonLibraryExample:

    # Basic communication

    def passing(self):
        pass
  
    def failing(self, message):
        raise AssertionError(message)

    def logging(self, message, level='INFO'):
        print '*%s* %s' % (level, message)

    def returning(self):
        return "returned string"

    # Arguments counts (Todo)

    def no_arguments(self):
        print 'No arguments'

    def one_argument(self, arg):
        print 'arg: %s' % arg

    def two_arguments(self, arg1, arg2):
        print '*INFO* arg1: %s' % arg1
        print '*INFO* arg2: %s' % arg2

    def arguments_with_default_values(self, arg1, arg2='two', arg3=42):
        print '%s | %s | %s' % (arg1, arg2, arg3)

    def variable_number_of_arguments(self, *args):
        return ' '.join(args)

    def required_defaults_and_varargs(self, req, default='world', *varargs):
        return ' '.join((req, default) + varargs)


    # Argument types (TODO)

    def argument_should_be_string(self, arg):
        self.argument_type_should_be(arg, basestring)

    def argument_should_be_integer(self, arg):
        self.argument_type_should_be(arg, int)

    def argument_should_be_float(self, arg):
        self.argument_type_should_be(arg, float)

    def argument_should_be_boolean(self, arg):
        self.argument_type_should_be(arg, bool)

    def argument_type_should_be(self, arg, type_):
        if not isinstance(arg, type_):
            raise AssertionError('Argument type should be %s but was %s'
                                 % (type_, type(arg)))

    # Return values

    def return_string(self):
        return 'Hello, world!'

    def return_unicode_string(self):
        return u'Hyv\xE4\xE4 \xFC\xF6t\xE4!'

    def return_empty_string(self):
        return ''

    def return_integer(self):
        return 42

    def return_negative_integer(self):
        return -1
  
    def return_float(self):
        return 3.14
  
    def return_negative_float(self):
        return -0.5

    def return_zero(self):
        return 0
  
    def return_boolean_true(self):
        return True

    def return_boolean_false(self):
        return False

    def return_nothing(self):
        pass

    def return__object(self):
        return MyObject()

    def return_list(self):
        return ['One', -2, False]

    def return_empty_list(self):
        return []

    def return_list_containing_none(self):
        return [None]

    def return_list_containing_objects(self):
        return [MyObject(1), MyObject(2)]

    def return_nested_list(self):
        return ['1', [2, [True]], [MyObject(), {'a':1,'b':2},
                                   (1,2,3), [None, [], (), {}]]]

    def return_tuple(self):
        return (1, 'two', True)

    def return_empty_tuple(self):
        return ()

    def return_nested_tuple(self):
        return ('1', (2, [True]), [MyObject(), (None, (), [], {})])

    def return_dictionary(self):
        return {'one': 1, 'true': True}

    def return_empty_dictionary(self):
        return {}

    def return_dictionary_with_non_string_keys(self):
        return {1: 2, False: True}

    def return_dictionary_containing_none(self):
        return {'As value': None, None: 'As key'}

    def return_dictionary_containing_objects(self):
        return {'As value': MyObject(1), MyObject(2): 'As key'}

    def return_nested_dictionary(self):
        return {1: {2: {3: {}}}, None: {True: MyObject(), 'list': [1,None,{}]}}

    # Not keywords

    def _private_method(self):
        pass

    def __private_method(self):
        pass

    attribute = 'Not a keyword'


class MyObject:
    def __init__(self, index=''):
        self.index = index
    def __str__(self):
        return '<MyObject%s>' % self.index


if __name__ == '__main__':
    from RobotRemoteServer import RobotRemoteServer
    RobotRemoteServer(PythonLibraryExample(), *sys.argv[1:])
