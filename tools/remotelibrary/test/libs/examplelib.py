import sys


class RemoteTestLibrary:

    _unicode = (u'Hyv\u00E4\u00E4 y\u00F6t\u00E4. '
                u'\u0421\u043F\u0430\u0441\u0438\u0431\u043E!')

    def get_server_language(self):
        lang = sys.platform.startswith('java') and 'jython' or 'python'
        return '%s%d%d' % (lang, sys.version_info[0], sys.version_info[1])

    # Basic communication (and documenting keywords)

    def passing(self):
        """This keyword passes.

        See `Failing`, `Logging`, and `Returning` for other basic keywords.
        """
        pass
  
    def failing(self, message):
        """This keyword fails with provided `message`"""
        raise AssertionError(message)

    def logging(self, message, level='INFO'):
        """This keywords logs given `message` with given `level`

        Example:
        | Logging | Hello, world! |      |
        | Logging | Warning!!!    | WARN |
        """
        print '*%s* %s' % (level, message)

    def returning(self):
        """This keyword returns a string 'returned string'."""
        return 'returned string'

    # Logging

    def one_message_without_level(self):
        print 'Hello, world!'

    def multiple_messages_with_different_levels(self):
        print 'Info message'
        print '*DEBUG* Debug message'
        print '*INFO* Second info'
        print 'this time with two lines'
        print '*INFO* Third info'
        print '*TRACE* This is ignored'
        print '*WARN* Warning'

    def log_unicode(self):
        print self._unicode
        
    def logging_and_failing(self):
        print '*INFO* This keyword will fail!'
        print '*WARN* Run for your lives!!'
        raise AssertionError('Too slow')

    def logging_and_returning(self):
        print 'Logged message'
        return 'Returned value'

    def log_control_char(self):
        print '\x01'

    # Failures

    def base_exception(self):
        raise Exception('My message')

    def exception_without_message(self):
        raise Exception

    def assertion_error(self):
        raise AssertionError('Failure message')

    def runtime_error(self):
        raise RuntimeError('Error message')

    def name_error(self):
        non_existing

    def attribute_error(self):
        self.non_existing

    def index_error(self):
        [][0]

    def zero_division(self):
        1/0

    def custom_exception(self):
        raise MyException('My message')

    def failure_deeper(self, rounds=10):
        if rounds == 1:
            raise RuntimeError('Finally failing')
        self.failure_deeper(rounds-1)

    # Arguments counts

    def no_arguments(self):
        return 'no arguments'

    def one_argument(self, arg):
        return arg

    def two_arguments(self, arg1, arg2):
        return '%s %s' % (arg1, arg2)

    def seven_arguments(self, arg1, arg2, arg3, arg4, arg5, arg6, arg7):
        return ' '.join((arg1, arg2, arg3, arg4, arg5, arg6, arg7))

    def arguments_with_default_values(self, arg1, arg2='2', arg3=3):
        return '%s %s %s' % (arg1, arg2, arg3)

    def variable_number_of_arguments(self, *args):
        return ' '.join(args)

    def required_defaults_and_varargs(self, req, default='world', *varargs):
        return ' '.join((req, default) + varargs)

    # Argument types

    def string_as_argument(self, arg):
        self._should_be_equal(arg, self.return_string())

    def unicode_string_as_argument(self, arg):
        self._should_be_equal(arg, self._unicode)

    def empty_string_as_argument(self, arg):
        self._should_be_equal(arg, '')

    def integer_as_argument(self, arg):
        self._should_be_equal(arg, self.return_integer())

    def negative_integer_as_argument(self, arg):
        self._should_be_equal(arg, self.return_negative_integer())

    def float_as_argument(self, arg):
        self._should_be_equal(arg, self.return_float())

    def negative_float_as_argument(self, arg):
        self._should_be_equal(arg, self.return_negative_float())

    def zero_as_argument(self, arg):
        self._should_be_equal(arg, 0)

    def boolean_true_as_argument(self, arg):
        self._should_be_equal(arg, True)

    def boolean_false_as_argument(self, arg):
        self._should_be_equal(arg, False)

    def none_as_argument(self, arg):
        self._should_be_equal(arg, '')

    def object_as_argument(self, arg):
        self._should_be_equal(arg, '<MyObject>')

    def list_as_argument(self, arg):
        self._should_be_equal(arg, self.return_list())

    def empty_list_as_argument(self, arg):
        self._should_be_equal(arg, [])

    def list_containing_none_as_argument(self, arg):
        self._should_be_equal(arg, [''])

    def list_containing_objects_as_argument(self, arg):
        self._should_be_equal(arg, ['<MyObject1>', '<MyObject2>'])

    def nested_list_as_argument(self, arg):
        exp = [ [True, False], [[1, '', '<MyObject>', {}]] ]
        self._should_be_equal(arg, exp)

    def dictionary_as_argument(self, arg):
        self._should_be_equal(arg, self.return_dictionary())

    def empty_dictionary_as_argument(self, arg):
        self._should_be_equal(arg, {})

    def dictionary_with_non_string_keys_as_argument(self, arg):
        self._should_be_equal(arg, {'1': 2, '': True})

    def dictionary_containing_none_as_argument(self, arg):
        self._should_be_equal(arg, {'As value': '', '': 'As key'})

    def dictionary_containing_objects_as_argument(self, arg):
        self._should_be_equal(arg, {'As value': '<MyObject1>', '<MyObject2>': 'As key'})

    def nested_dictionary_as_argument(self, arg):
        exp = { '1': {'': False},
                '2': {'A': {'n': ''}, 'B': {'o': '<MyObject>', 'e': {}}} }
        self._should_be_equal(arg, exp)

    def _should_be_equal(self, arg, exp):
        if arg != exp:
            raise AssertionError('%r != %r' % (arg, exp))

    # Return values

    def return_string(self):
        return 'Hello, world!'

    def return_unicode_string(self):
        return self._unicode

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

    def return_object(self):
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
        return [ [True, False], [[1, None, MyObject(), {}]] ]

    def return_tuple(self):
        return (1, 'two', True)

    def return_empty_tuple(self):
        return ()

    def return_nested_tuple(self):
        return ( (True, False), [(1, None, MyObject(), {})] )

    def return_dictionary(self):
        return {'one': 1, 'spam': 'eggs'}

    def return_empty_dictionary(self):
        return {}

    def return_dictionary_with_non_string_keys(self):
        return {1: 2, None: True}

    def return_dictionary_containing_none(self):
        return {'As value': None, None: 'As key'}

    def return_dictionary_containing_objects(self):
        return {'As value': MyObject(1), MyObject(2): 'As key'}

    def return_nested_dictionary(self):
        return { 1: {None: False},
                 2: {'A': {'n': None}, 'B': {'o': MyObject(), 'e': {}}} }

    def return_control_char(self):
        return '\x01'

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

class MyException(Exception):
    pass


if __name__ == '__main__':
    import sys
    from robotremoteserver import RobotRemoteServer

    RobotRemoteServer(RemoteTestLibrary(), *sys.argv[1:])
