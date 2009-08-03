import unittest

from robot.running.userkeyword import EmbeddedArgsUserHandler
from robot.utils.asserts import *


class HandlerDataMock:
    
    def __init__(self, name, args=[]):
        self.name = name
        self.args = args
        self.metadata = {}
        self.keywords = []
        self.defaults = []
        self.varargs = None
        self.minargs = 0
        self.maxargs = 0
        self.return_value = None
        
        
def EAUH(*args):
    return EmbeddedArgsUserHandler(HandlerDataMock(*args), None)

    
class TestEmbeddedArgsUserHandler(unittest.TestCase):

    def test_keyword_has_normal_arguments(self):  
        assert_raises(TypeError, EAUH, 'Name has ${args}', ['${norm arg}'])
  
    def test_no_embedded_args(self):
        assert_raises(TypeError, EAUH, 'No embedded args here')
    
    def test_get_embedded_arg_and_regexp(self):
        handler = EAUH('User selects ${item} from list')
        assert_equals(handler._embedded_args, ['${item}'])
        assert_equals(handler._name_regexp.pattern, 
                      '^User\\ selects\\ (.*?)\\ from\\ list$')

    def test_get_multiple_embedded_args_and_regexp(self):
        handler = EAUH('${x} selects ${y} from ${z}')
        assert_equals(handler._embedded_args, ['${x}', '${y}', '${z}'])
        assert_equals(handler._name_regexp.pattern, 
                      '^(.*?)\\ selects\\ (.*?)\\ from\\ (.*?)$')

    def test_get_matching_handler_when_no_match(self):
        handler = EAUH('User selects ${item}')
        assert_equals(handler.get_matching_handler('Not matching'), None)
    
    def test_get_matching_handler_when_one_variable_matches(self):
        handler = EAUH('User selects ${item}')
        runnable_handler = handler.get_matching_handler('User selects book')
        assert_equals(runnable_handler._args_values, ('book',))

    def test_get_matching_handler_return_deepcopy_of_the_handler(self):
        handler = EAUH('User selects ${item}')
        runnable_handler = handler.get_matching_handler('User selects book')
        assert_not_equals(handler, runnable_handler)
        


if __name__ == '__main__':
    unittest.main()
