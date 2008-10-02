import unittest
import sys
    
from robot.variables import variables, is_list_var, is_scalar_var, is_var
from robot.errors import *
from robot import utils
from robot.utils.asserts import *


SCALARS = [ '${var}', '${  v A  R }' ]
LISTS = [ '@{var}', '@{  v A  R }' ]
NOKS = [ 'var', '$var', '${var', '${va}r', '@{va}r', '@var', '%{var}',
         ' ${var}', '@{var} ', '\\${var}', '\\\\${var}' ]



# Simple objects needed when testing assigning objects to variables.
# JavaObject lives in '../../acceptance/testdata/libraries'

class PythonObject:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __str__(self):
        return '(%s, %s)' % (self.a, self.b)
    __repr__ = __str__

if utils.is_jython: 
    import JavaObject    



class TestIsMethods(unittest.TestCase):
    
    def test_is_var(self):
        for ok in SCALARS + LISTS:
            assert is_var(ok)
        for nok in NOKS:
            assert not is_var(nok)
    
    def test_is_scalar_var(self):
        for ok in SCALARS:
            assert is_scalar_var(ok)
        for nok in LISTS + NOKS:
            assert not is_scalar_var(nok)
    
    def test_is_list_var(self):
        for ok in LISTS:
            assert is_list_var(ok)
        for nok in SCALARS + NOKS:
            assert not is_list_var(nok)
            

class TestVariables(unittest.TestCase):

    def setUp(self):
        self.varz = variables.Variables()

    def test_set(self):
        for var in SCALARS + LISTS:
            assert not self.varz.has_key(var)
            self.varz[var] = ['value']
            assert self.varz.has_key(var), var
            assert self.varz.has_key(var.lower().replace(' ',''))
            self.varz.clear()

    def test_set_invalid(self):
        for var in NOKS:
            try:
                self.varz[var] = ['value']
            except DataError:
                pass
            else:
                fail()

    def test_set_scalar(self):
        for var in SCALARS:
            for value in [ 'str', 10, ['hi','u'], ['hi',2], {'a':1,'b':2}, self,
                           None, unittest.TestCase ]:
                self.varz[var] = value
                act = self.varz[var]
                assert act == value, '%s: %s %s != %s %s' \
                        % (var, act, type(act), value, type(value))
                self.varz.clear()
        self.varz['${myvar}'] = ''
        assert_equals(self.varz['${myvar}'], '')
                
    def test_set_list(self):
        for var in LISTS:
            for value in [ [], [''], ['str'], [10], ['hi','u'], ['hi',2], 
                           [{'a':1,'b':2}, self, None] ]:
                self.varz[var] = value
                assert_equals(self.varz[var], value)
                self.varz.clear()

    def test_getitem_invalid(self):
        for var in NOKS:
            self.assertRaises(DataError, self.varz.__getitem__, var)

    def test_has_key(self):
        # tested mainly in test_setitem
        assert not self.varz.has_key('${non-existing}')

    def test_replace_scalar(self):
        self.varz['${foo}'] = 'bar'
        self.varz['${a}'] = 'ari'
        for inp, exp in [ ('${foo}','bar'), ('${a}','ari'),
                          ('${a','${a'), ('',''), ('hii','hii'),
                          ("Let's go to ${foo}!", "Let's go to bar!"),
                          ('${foo}ba${a}-${a}', 'barbaari-ari') ]:
            assert_equals(self.varz.replace_scalar(inp), exp)

    def test_replace_list(self):
        self.varz['@{L}'] = ['v1','v2']
        self.varz['@{E}'] = []
        self.varz['@{S}'] = ['1','2','3']
        for inp, exp in [ (['@{L}'], ['v1','v2']),
                          (['@{L}','v3'], ['v1','v2','v3']),
                          (['v0','@{L}','@{E}','v@{S}[2]'], ['v0','v1','v2','v3']),
                          ([], []), (['hi u','hi 2',3], ['hi u','hi 2',3]) ]:
            assert_equals(self.varz.replace_list(inp), exp)

    def test_replace_list_in_scalar_context(self):
        self.varz['@{list}'] = ['v1','v2']
        assert_equals(self.varz.replace_list(['@{list}']), ['v1', 'v2'])
        assert_equals(self.varz.replace_list(['-@{list}-']), ["-['v1', 'v2']-"])

    def test_replace_list_item(self):
        self.varz['@{L}'] = ['v0','v1']
        assert_equal(self.varz.replace_list(['@{L}[0]']), ['v0'])
        assert_equal(self.varz.replace_scalar('@{L}[1]'), 'v1')
        assert_equal(self.varz.replace_scalar('-@{L}[0]@{L}[1]@{L}[0]-'), '-v0v1v0-')
        self.varz['@{L2}'] = ['v0',['v11','v12']]
        assert_equal(self.varz.replace_list(['@{L2}[0]']), ['v0'])
        assert_equal(self.varz.replace_list(['@{L2}[1]']), [['v11','v12']])
        assert_equal(self.varz.replace_scalar('@{L2}[0]'), 'v0')
        assert_equal(self.varz.replace_scalar('@{L2}[1]'), ['v11','v12'])
        assert_equal(self.varz.replace_list(['@{L}[0]','@{L2}[1]']), ['v0',['v11','v12']])

    def test_replace_non_strings(self):
        self.varz['${d}'] = {'a':1,'b':2}
        self.varz['${n}'] = None
        assert_equal(self.varz.replace_scalar('${d}'), {'a':1,'b':2})
        assert_equal(self.varz.replace_scalar('${n}'), None)
        
    def test_replace_non_strings_inside_string(self):
        class Example:
            def __str__(self):
                return 'Hello'
        self.varz['${h}'] = Example()
        self.varz['${w}'] = 'world'
        res = self.varz.replace_scalar('Another "${h} ${w}" example')
        assert_equals(res, 'Another "Hello world" example')

    def test_replace_list_item_invalid(self):
        self.varz['@{L}'] = ['v0','v1','v3']
        for inv in [ '@{L}[3]', '@{NON}[0]', '@{L[2]}' ]:
            self.assertRaises(DataError, self.varz.replace_list, [inv])
                        
    def test_replace_non_existing_list(self):
        self.assertRaises(DataError, self.varz.replace_list, ['${nonexisting}'])

    def test_replace_non_existing_scalar(self):
        self.assertRaises(DataError, self.varz.replace_scalar, '${nonexisting}')
        
    def test_replace_non_existing_string(self):
        self.assertRaises(DataError, self.varz.replace_string, '${nonexisting}')
        
    def test_replace_escaped(self):
        self.varz['${foo}'] = 'bar'
        for inp, exp in [ (r'\${foo}', r'${foo}'),
                          (r'\\${foo}', r'\bar'),
                          (r'\\\${foo}', r'\${foo}'),
                          (r'\\\\${foo}', r'\\bar'), 
                          (r'\\\\\${foo}', r'\\${foo}') ]:
            assert_equals(self.varz.replace_scalar(inp), exp)

    def test_variables_in_value(self):
        self.varz['${exists}'] = 'Variable exists but is still not replaced'
        self.varz['${test}'] = '${exists} & ${does_not_exist}'
        assert_equals(self.varz['${test}'], '${exists} & ${does_not_exist}')
        self.varz['@{test}'] = ['${exists}', '&', '${does_not_exist}']
        assert_equals(self.varz['@{test}'], '${exists} & ${does_not_exist}'.split())
        
    def test_variable_as_object(self):
        obj = PythonObject('a', 1)
        self.varz['${obj}'] = obj
        assert_equals(self.varz['${obj}'], obj)
        expected = ['Some text here %s and %s there' % (obj,obj)]
        actual = self.varz.replace_list(['Some text here ${obj} and ${obj} there'])
        assert_equals(actual, expected)
                
    def test_extended_variables(self):
        # Extended variables are vars like ${obj.name} when we have var ${obj}
        obj = PythonObject('a', [1,2,3])
        dic = { 'a': 1, 'o': obj }
        self.varz['${obj}'] = obj
        self.varz['${dic}'] = dic
        assert_equals(self.varz.replace_scalar('${obj.a}'), 'a')
        assert_equals(self.varz.replace_scalar('${obj.b}'), [1,2,3])
        assert_equals(self.varz.replace_scalar('${obj.b[0]}-${obj.b[1]}'), '1-2')
        assert_equals(self.varz.replace_scalar('${dic["a"]}'), 1)
        assert_equals(self.varz.replace_scalar('${dic["o"]}'), obj)
        assert_equals(self.varz.replace_scalar('-${dic["o"].b[2]}-'), '-3-')
        
    def test_internal_variables(self):
        # Internal variables are variables like ${my${name}}
        self.varz['${name}'] = 'name'
        self.varz['${my name}'] = 'value'
        assert_equals(self.varz.replace_scalar('${my${name}}'), 'value')
        self.varz['${whos name}'] = 'my'
        assert_equals(self.varz.replace_scalar('${${whos name} ${name}}'), 'value')
        assert_equals(self.varz.replace_scalar('${${whos${name}}${name}}'), 'value') 
        self.varz['${my name}'] = [1,2,3]
        assert_equals(self.varz.replace_scalar('${${whos${name}}${name}}'), [1,2,3])
        assert_equals(self.varz.replace_scalar('- ${${whos${name}}${name}} -'), '- [1, 2, 3] -')
        
    def test_list_variable_as_scalar(self):
        self.varz['@{name}'] = exp = ['spam', 'eggs']
        assert_equals(self.varz.replace_scalar('${name}'), exp)
        assert_equals(self.varz.replace_list(['${name}', 42]), [exp, 42])
        assert_equals(self.varz.replace_string('${name}'), str(exp))
        assert_true(self.varz.has_key('${name}'))

    if utils.is_jython:
        
        def test_variable_as_object_in_java(self):
            obj = JavaObject('hello')
            self.varz['${obj}'] = obj    
            assert_equals(self.varz['${obj}'], obj)
            assert_equals(self.varz.replace_scalar('${obj} world'), 'hello world')
        
        def test_extended_variables_in_java(self):
            obj = JavaObject('my name')
            self.varz['${obj}'] = obj
            assert_equals(self.varz.replace_list(['${obj.name}']), ['my name'])



class TestVariableSplitter(unittest.TestCase):
        
    _identifiers = ['$','@','%','&','*']

    def test_empty(self):
        self._test('', None)

    def test_no_vars(self):
        for inp in ['hello world', '$hello', '{hello}', '$\\{hello}',
                    '${hello', '$hello}' ]:
            self._test(inp, None)
        
    def test_backslashes(self):
        for inp in ['\\', '\\\\', '\\\\\\\\\\',
                    '\\hello\\\\world\\\\\\']:
            self._test(inp, None)
        
    def test_one_var(self):
        self._test('${hello}', '${hello}', 0)
        self._test('1 @{hello} more', '@{hello}', 2)
        self._test('*{hi}}', '*{hi}', 0)
        self._test('{%{{hi}}', '%{{hi}', 1)
        self._test('-= ${} =-', '${}', 3)
        # In this case splitter thinks there are internal but there aren't.
        # Better check would probably spent more time than that is saved when
        # variable base is processed again in this special case.
        self._test('%{hi%{u}', '%{hi%{u}', 0, internal=True)  
        
    def test_multiple_vars(self):
        self._test('${hello} ${world}', '${hello}', 0)
        self._test('hi %{u}2 and @{u2} and also *{us3}', '%{u}', 3)
        self._test('0123456789 %{1} and @{2', '%{1}', 11)

    def test_escaped_var(self):
        self._test('\\${hello}', None)
        self._test('hi \\\\\\${hello} moi', None)
        
    def test_not_escaped_var(self):
        self._test('\\\\${hello}', '${hello}', 2)
        self._test('\\hi \\\\\\\\\\\\${hello} moi', '${hello}',
                   len('\\hi \\\\\\\\\\\\'))
        self._test('\\ ${hello}', '${hello}', 2)
        self._test('${hello}\\', '${hello}', 0)
        self._test('\\ \\ ${hel\\lo}\\', '${hel\\lo}', 4)
        
    def test_escaped_and_not_escaped_vars(self):
        for inp, var, start in [ 
                ('\\${esc} ${not}', '${not}', len('\\${esc} ')),
                ('\\\\\\${esc} \\\\${not}', '${not}',
                 len('\\\\\\${esc} \\\\')),
                ('\\${esc}\\\\${not}${n2}', '${not}', len('\\${esc}\\\\')) ]:
            self._test(inp, var, start)
            
    def test_internal_vars(self):
        for inp, var, start in [
                ('${hello${hi}}', '${hello${hi}}', 0),
                ('bef ${${hi}hello} aft', '${${hi}hello}', 4),
                ('\\${not} ${hel${hi}lo} ', '${hel${hi}lo}', len('\\${not} ')),
                ('${${hi}${hi}}\\', '${${hi}${hi}}', 0),
                ('${${hi${hi}}} ${xx}', '${${hi${hi}}}', 0),
                ('${xx} ${${hi${hi}}}', '${xx}', 0),
                ('${\\${hi${hi}}}', '${\\${hi${hi}}}', 0),
                ('\\${${hi${hi}}}', '${hi${hi}}', len('\\${')),
                ('\\${\\${hi\\\\${hi}}}', '${hi}', len('\\${\\${hi\\\\')) ]:
            internal = var.count('{') > 1
            self._test(inp, var, start, internal=internal)
        
    def test_index(self):
        self._test('@{x}[0]', '@{x}', 0, '0')
        self._test('.@{x}[42]..', '@{x}', 1, '42')
        self._test('@{x}[${i}] ${xyz}', '@{x}', 0, '${i}')
        self._test('@{x}[]', '@{x}', 0, '')
        self._test('@{x}[inv]', '@{x}', 0, 'inv')
        self._test('@{x}[0', '@{x}', 0, None)
        self._test('@{x}}[0]', '@{x}', 0, None)
        self._test('${x}[0]', '${x}', 0, None)
        self._test('%{x}[0]', '%{x}', 0, None)
        self._test('*{x}[0]', '*{x}', 0, None)
        self._test('&{x}[0]', '&{x}', 0, None)
                
    def test_custom_identifiers(self):
        for inp, start in [ ('@{x}${y}', 4),
                            ('%{x} ${y}', 5),
                            ('*{x}567890${y}', 10),
                            ('&{x}%{x}@{x}\\${x}${y}', 
                             len('&{x}%{x}@{x}\\${x}')) ]:
            self._test(inp, '${y}', start, identifiers=['$'])

    def test_identifier_as_variable_name(self):
        for ident in self._identifiers:
            var = '${%s}' % ident
            self._test(var, var)
            self._test(var+'spam', var)
            self._test(var+'{eggs}', var)
                                
    def _test(self, inp, variable, start=0, index=None, identifiers=None,
              internal=False):
        if variable is not None:
            identifier = variable[0]
            base = variable[2:-1]
            end = start + len(variable)
            if index is not None:
                end += len(index) + 2
        else:
            identifier = base = None
            start = end = -1
        if not identifiers:
            identifiers = self._identifiers
        res = variables._VariableSplitter(inp, identifiers)
        assert_equals(res.base, base, inp+' base')
        assert_equals(res.start, start, inp+' start')
        assert_equals(res.end, end, inp+' end')
        assert_equals(res.identifier, identifier, inp+' indentifier')
        assert_equals(res.index, index, inp+' index')
        assert_equals(res.may_have_internal_variables, internal,
                      inp+'internal')


if __name__ == '__main__':
    unittest.main()
