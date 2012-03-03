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

    def test_update(self):
        self.varz['${a}'] = 1
        self.varz.update({'${b}':2})
        for k, v in [('${a}', 1), ('${b}', 2)]:
            assert_true(k in self.varz)
            assert_true(k in self.varz.keys())
            assert_equals(self.varz[k], v)

    def test_update_invalid(self):
        self.varz['${a}'] = 1
        assert_raises(DataError, self.varz.update, {'invalid variable name':2})

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
        self.varz['${k}'] = 'v'
        assert self.varz.has_key('${k}')
        assert self.varz.has_key('${1}')
        assert self.varz.has_key('${k.upper()}')
        assert not self.varz.has_key('${non-existing}')

    def test__contains__(self):
        self.varz['${k}'] = 'v'
        assert '${k}' in self.varz
        assert '${-3}' in self.varz
        assert '${k.upper()}' in self.varz
        assert '${nok}' not in self.varz

    def test_contains_(self):
        self.varz['${k}'] = 'v'
        assert self.varz.contains('${k}')
        assert self.varz.contains('${ K }')
        assert not self.varz.contains('${-3}')
        assert self.varz.contains('${-3}', extended=True)
        assert not self.varz.contains('${k.upper()}')
        assert self.varz.contains('${k.upper()}', extended=True)
        assert not self.varz.contains('${nok}')
        assert not self.varz.contains('${nok)}', extended=True)

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

    def test_space_is_not_ignored_after_newline_in_extend_variable_syntax(self):
        self.varz['${x}'] = 'test string'
        self.varz['${lf}'] = '\\n'
        self.varz['${lfs}'] = '\\n '
        for inp, exp in [('${x.replace(" ", """\\n""")}', 'test\nstring'),
                         ('${x.replace(" ", """\\n """)}', 'test\n string'),
                         ('${x.replace(" ", """${lf}""")}', 'test\nstring'),
                         ('${x.replace(" ", """${lfs}""")}', 'test\n string')]:
            assert_equals(self.varz.replace_scalar(inp), exp)

    def test_escaping_with_extended_variable_syntax(self):
        self.varz['${p}'] = 'c:\\temp'
        assert self.varz['${p}'] == 'c:\\temp'
        assert_equals(self.varz.replace_scalar('${p + "\\\\foo.txt"}'),
                      'c:\\temp\\foo.txt')

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

    def test_math_with_internal_vars(self):
        assert_equals(self.varz.replace_scalar('${${1}+${2}}'), 3)
        assert_equals(self.varz.replace_scalar('${${1}-${2}}'), -1)
        assert_equals(self.varz.replace_scalar('${${1}*${2}}'), 2)
        assert_equals(self.varz.replace_scalar('${${1}/${2}}'), 0)

    def test_math_with_internal_vars_with_spaces(self):
        assert_equals(self.varz.replace_scalar('${${1} + ${2.5}}'), 3.5)
        assert_equals(self.varz.replace_scalar('${${1} - ${2} + 1}'), 0)
        assert_equals(self.varz.replace_scalar('${${1} * ${2} - 1}'), 1)
        assert_equals(self.varz.replace_scalar('${${1} / ${2.0}}'), 0.5)

    def test_math_with_internal_vars_does_not_work_if_first_var_is_float(self):
        assert_raises(DataError, self.varz.replace_scalar, '${${1.1}+${2}}')
        assert_raises(DataError, self.varz.replace_scalar, '${${1.1} - ${2}}')
        assert_raises(DataError, self.varz.replace_scalar, '${${1.1} * ${2}}')
        assert_raises(DataError, self.varz.replace_scalar, '${${1.1}/${2}}')

    def test_list_variable_as_scalar(self):
        self.varz['@{name}'] = exp = ['spam', 'eggs']
        assert_equals(self.varz.replace_scalar('${name}'), exp)
        assert_equals(self.varz.replace_list(['${name}', 42]), [exp, 42])
        assert_equals(self.varz.replace_string('${name}'), str(exp))
        assert_true(self.varz.has_key('${name}'))

    def test_copy(self):
        varz = variables.Variables(identifiers=['$'])
        varz['${foo}'] = 'bar'
        copy = varz.copy()
        assert_equals(copy['${foo}'], 'bar')
        assert_equals(copy._identifiers, ['$'])

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


if __name__ == '__main__':
    unittest.main()
