import unittest

from robot.running.userkeyword import UserHandler, EmbeddedArgsTemplate, \
        EmbeddedArgs
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
        
        
def EAT(*args):
    return EmbeddedArgsTemplate(HandlerDataMock(*args), None)

    
class TestEmbeddedArgs(unittest.TestCase):

    def setUp(self):
        self.tmp1 = EAT('User selects ${item} from list')
        self.tmp2 = EAT('${x} * ${y} from "${z}"')

    def test_keyword_has_normal_arguments(self):  
        assert_raises(TypeError, EAT, 'Name has ${args}', ['${norm arg}'])
  
    def test_no_embedded_args(self):
        assert_raises(TypeError, EAT, 'No embedded args here')
    
    def test_get_embedded_arg_and_regexp(self):
        assert_equals(self.tmp1.embedded_args, ['${item}'])
        assert_equals(self.tmp1.name_regexp.pattern, 
                      '^User\\ selects\\ (.*?)\\ from\\ list$')

    def test_get_multiple_embedded_args_and_regexp(self):
        assert_equals(self.tmp2.embedded_args, ['${x}', '${y}', '${z}'])
        assert_equals(self.tmp2.name_regexp.pattern, 
                      '^(.*?)\\ \\*\\ (.*?)\\ from\\ \\"(.*?)\\"$')

    def test_create_handler_when_no_match(self):
        assert_raises(TypeError, EmbeddedArgs, 'Not matching', self.tmp1)
    
    def test_create_handler_with_one_embedded_arg(self):
        handler = EmbeddedArgs('User selects book from list', self.tmp1)
        assert_equals(handler.embedded_args, [('${item}', 'book')])
        handler = EmbeddedArgs('User selects radio from list', self.tmp1)
        assert_equals(handler.embedded_args, [('${item}', 'radio')])

    def test_create_handler_with_many_embedded_args(self):
        handler = EmbeddedArgs('User * book from "list"', self.tmp2)
        assert_equals(handler.embedded_args, 
                      [('${x}', 'User'), ('${y}', 'book'), ('${z}', 'list')])

    def test_create_handler_with_empty_embedded_arg(self):
        handler = EmbeddedArgs('User selects  from list', self.tmp1)
        assert_equals(handler.embedded_args, [('${item}', '')])

    def test_create_handler_with_special_characters_in_embedded_args(self):
        handler = EmbeddedArgs('Janne & Heikki * "enjoy" from """', self.tmp2)
        assert_equals(handler.embedded_args, 
                      [('${x}', 'Janne & Heikki'), ('${y}', '"enjoy"'), ('${z}', '"')])

    def test_embedded_args_without_separators(self):
        template = EAT('This ${does}${not} work so well')
        handler = EmbeddedArgs('This doesnot work so well', template) 
        assert_equals(handler.embedded_args, 
                      [('${does}', ''), ('${not}', 'doesnot')])

    def test_embedded_args_with_separators_in_values(self):
        template = EAT('This ${could} ${work}-${OK}')
        handler = EmbeddedArgs("This doesn't really work---", template) 
        assert_equals(handler.embedded_args, 
                      [('${could}', "doesn't"), ('${work}', 'really work'), ('${OK}', '--')])

    def test_embedded_args_handler_has_all_needed_attributes(self):
        normal = UserHandler(HandlerDataMock('My name'), None)
        embedded = EmbeddedArgs('My name', EAT('My ${name}'))
        for attr in dir(normal):
            assert_true(hasattr(embedded, attr), "'%s' missing" % attr)


if __name__ == '__main__':
    unittest.main()
