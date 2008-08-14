import os.path
import sys
import types

class MyLibrary:
  
    def divide(self, a, b):
        return a / b
  
    def raise_failure(self, message):
        raise AssertionError(message)
  
    def logging(self, message, message_level='INFO'):
        print '*' + message_level + '* ' + message
  
    def return_nothing(self):
        return None
      
    def return_multiple_values(self, value1, value2):
        return value1, value2
  
    def check_argument_is_boolean_type_true(self, arg):
        self.arguments_type_should_be(arg, True.__class__)
        return arg
  
    def return_true():
        return True

    def check_argument_is_string_type(self, arg):
        self.arguments_type_should_be(arg, types.StringType)
        return arg

    def arguments_type_should_be(self, arg, type):
        if not arg.__class__ == type:
            raise Exception, 'Arguments type should be '+ type +' but was ' + arg.__class__
  
    def should_be_list(self, arg):
        if arg != ['a','b','c']:
            raise AsserionError, "Given list is not ['a', 'b', 'c']"
        return arg
  
    def should_be_dictionary(self, arg):
        if arg != {'a':1, 'b':'Hello', 'c':['a', 1]}:
            raise AssertionError, "Given argument is not {'a'=> 1, 'b'=>'Hello', 'c' => ['a', 1]}"
        return arg
  
    def return_object(self):
        return  MyObject()


class MyObject:
    def __str__(self):
        return "String representation of MyObject"

#METHODS FOR STARTING THE LIBRARY FROM COMMAND LINE

def start(port):
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    from RobotXMLRPCServer import RobotXMLRPCServer
    
    server = RobotXMLRPCServer(MyLibrary(), port)
    server.register_function(server.get_keyword_names)
    server.register_function(server.run_keyword)
    server.register_introspection_functions()
    server.serve_forever()

def help():
    print """
  Usage: %s port"
""" % (__file__)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        help()
    else:
        start(int(sys.argv[1]))
