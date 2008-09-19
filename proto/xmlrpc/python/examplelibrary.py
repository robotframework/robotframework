import os.path
import sys
import types


class PythonLibraryExample:

    def do_nothing(self):
        pass
  
    def failure(self, message):
        raise AssertionError(message)

    def error(self):
        1/0
  
    def logging(self, message, level='INFO'):
        print '*%s* %s' % (level, message)

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

    def return_string(self):
        return 'Hello, world!'

    def return_integer(self):
        return 42
  
    def return_float(self):
        return -0.5
  
    def return_boolean(self):
        return true

    def return_multiple_values(self, given):
        return 'first', 2, -3.14, given

    def return_object(self):
        return MyObjectToReturn()

    def _private_method(self):
        pass

    def __private_method(self):
        pass


class MyObjectToReturn:
  def __str__(self):
    return "String representation of MyObjectToReturn"


if __name__ == '__main__':
    if len(sys.argv) == 2:
        from RobotXMLRPCServer import RobotXmlRpcServer
        RobotXmlRpcServer(PythonLibraryExample(), sys.argv[1])
    else:
        print 'Usage: %s port' % sys.argv[0]
