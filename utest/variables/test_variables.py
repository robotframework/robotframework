import unittest

from robot.variables import Variables
from robot.errors import DataError, VariableError
from robot.utils.asserts import assert_equal, assert_raises


SCALARS = ['${var}', '${  v A  R }']
LISTS = ['@{var}', '@{  v A  R }']
NOKS = ['var', '$var', '${var', '${va}r', '@{va}r', '@var', '%{var}', ' ${var}',
        '@{var} ', '\\${var}', '\\\\${var}', 42, None, ['${var}'], DataError]


class PythonObject(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __getitem__(self, index):
        return (self.a, self.b)[index]
    def __str__(self):
        return '(%s, %s)' % (self.a, self.b)
    def __len__(self):
        return 2
    __repr__ = __str__


class TestVariables(unittest.TestCase):

    def setUp(self):
        self.varz = Variables()

    def test_set(self):
        value = ['value']
        for var in SCALARS + LISTS:
            self.varz[var] = value
            assert_equal(self.varz[var], value)
            assert_equal(self.varz[var.lower().replace(' ', '')], value)
            self.varz.clear()

    def test_set_invalid(self):
        for var in NOKS:
            assert_raises(DataError, self.varz.__setitem__, var, 'value')

    def test_set_scalar(self):
        for var in SCALARS:
            for value in ['string', '', 10, ['hi', 'u'], ['hi', 2],
                          {'a': 1, 'b': 2}, self, None, unittest.TestCase]:
                self.varz[var] = value
                assert_equal(self.varz[var], value)

    def test_set_list(self):
        for var in LISTS:
            for value in [[], [''], ['str'], [10], ['hi', 'u'], ['hi', 2],
                          [{'a': 1, 'b': 2}, self, None]]:
                self.varz[var] = value
                assert_equal(self.varz[var], value)
                self.varz.clear()

    def test_replace_scalar(self):
        self.varz['${foo}'] = 'bar'
        self.varz['${a}'] = 'ari'
        for inp, exp in [('${foo}', 'bar'),
                         ('${a}', 'ari'),
                         (r'$\{a}', '${a}'),
                         ('', ''),
                         ('hii', 'hii'),
                         ("Let's go to ${foo}!", "Let's go to bar!"),
                         ('${foo}ba${a}-${a}', 'barbaari-ari')]:
            assert_equal(self.varz.replace_scalar(inp), exp)

    def test_replace_list(self):
        self.varz['@{L}'] = ['v1', 'v2']
        self.varz['@{E}'] = []
        self.varz['@{S}'] = ['1', '2', '3']
        for inp, exp in [(['@{L}'], ['v1', 'v2']),
                         (['@{L}', 'v3'], ['v1', 'v2', 'v3']),
                         (['v0', '@{L}', '@{E}', 'v${S}[2]'], ['v0', 'v1', 'v2', 'v3']),
                         ([], []),
                         (['hi u', 'hi 2', 3], ['hi u','hi 2', 3])]:
            assert_equal(self.varz.replace_list(inp), exp)

    def test_replace_list_in_scalar_context(self):
        self.varz['@{list}'] = ['v1', 'v2']
        assert_equal(self.varz.replace_list(['@{list}']), ['v1', 'v2'])
        assert_equal(self.varz.replace_list(['-@{list}-']), ["-['v1', 'v2']-"])

    def test_replace_list_item(self):
        self.varz['@{L}'] = ['v0', 'v1']
        assert_equal(self.varz.replace_list(['${L}[0]']), ['v0'])
        assert_equal(self.varz.replace_scalar('${L}[1]'), 'v1')
        assert_equal(self.varz.replace_scalar('-${L}[0]${L}[1]${L}[0]-'), '-v0v1v0-')
        self.varz['${L2}'] = ['v0', ['v11', 'v12']]
        assert_equal(self.varz.replace_list(['${L2}[0]']), ['v0'])
        assert_equal(self.varz.replace_list(['${L2}[1]']), [['v11', 'v12']])
        assert_equal(self.varz.replace_scalar('${L2}[0]'), 'v0')
        assert_equal(self.varz.replace_scalar('${L2}[1]'), ['v11', 'v12'])
        assert_equal(self.varz.replace_list(['${L}[0]', '@{L2}[1]']), ['v0', 'v11', 'v12'])

    def test_replace_dict_item(self):
        self.varz['&{D}'] = {'a': 1, 2: 'b', 'nested': {'a': 1}}
        assert_equal(self.varz.replace_scalar('${D}[a]'), 1)
        assert_equal(self.varz.replace_scalar('${D}[${2}]'), 'b')
        assert_equal(self.varz.replace_scalar('${D}[nested][a]'), 1)
        assert_equal(self.varz.replace_scalar('${D}[nested]'), {'a': 1})
        assert_equal(self.varz.replace_scalar('&{D}[nested]'), {'a': 1})

    def test_replace_non_strings(self):
        self.varz['${d}'] = {'a': 1, 'b': 2}
        self.varz['${n}'] = None
        assert_equal(self.varz.replace_scalar('${d}'), {'a': 1, 'b': 2})
        assert_equal(self.varz.replace_scalar('${n}'), None)

    def test_replace_non_strings_inside_string(self):
        class Example:
            def __str__(self):
                return 'Hello'
        self.varz['${h}'] = Example()
        self.varz['${w}'] = 'world'
        res = self.varz.replace_scalar('Another "${h} ${w}" example')
        assert_equal(res, 'Another "Hello world" example')

    def test_replace_list_item_invalid(self):
        self.varz['@{L}'] = ['v0', 'v1', 'v3']
        for inv in ['@{L}[3]', '@{NON}[0]', '@{L[2]}']:
            assert_raises(VariableError, self.varz.replace_list, [inv])

    def test_replace_non_existing_list(self):
        assert_raises(VariableError, self.varz.replace_list, ['${nonexisting}'])

    def test_replace_non_existing_scalar(self):
        assert_raises(VariableError, self.varz.replace_scalar, '${nonexisting}')

    def test_replace_non_existing_string(self):
        assert_raises(VariableError, self.varz.replace_string, '${nonexisting}')

    def test_non_string_input(self):
        for item in [1, False, None, [], (), {}, object]:
            assert_equal(self.varz.replace_list([item]), [item])
            assert_equal(self.varz.replace_scalar(item), item)
            assert_equal(self.varz.replace_string(item), str(item))

    def test_replace_escaped(self):
        self.varz['${foo}'] = 'bar'
        for inp, exp in [(r'\${foo}', r'${foo}'),
                         (r'\\${foo}', r'\bar'),
                         (r'\\\${foo}', r'\${foo}'),
                         (r'\\\\${foo}', r'\\bar'),
                         (r'\\\\\${foo}', r'\\${foo}')]:
            assert_equal(self.varz.replace_scalar(inp), exp)

    def test_variables_in_value(self):
        self.varz['${exists}'] = 'Variable exists but is still not replaced'
        self.varz['${test}'] = '${exists} & ${does_not_exist}'
        assert_equal(self.varz['${test}'], '${exists} & ${does_not_exist}')
        self.varz['@{test}'] = ['${exists}', '&', '${does_not_exist}']
        assert_equal(self.varz['@{test}'], '${exists} & ${does_not_exist}'.split())

    def test_variable_as_object(self):
        obj = PythonObject('a', 1)
        self.varz['${obj}'] = obj
        assert_equal(self.varz['${obj}'], obj)
        expected = ['Some text here %s and %s there' % (obj, obj)]
        actual = self.varz.replace_list(['Some text here ${obj} and ${obj} there'])
        assert_equal(actual, expected)

    def test_extended_variables(self):
        # Extended variables are vars like ${obj.name} when we have var ${obj}
        obj = PythonObject('a', [1, 2, 3])
        dic = {'a': 1, 'o': obj}
        self.varz['${obj}'] = obj
        self.varz['${dic}'] = dic
        assert_equal(self.varz.replace_scalar('${obj.a}'), 'a')
        assert_equal(self.varz.replace_scalar('${obj.b}'), [1, 2, 3])
        assert_equal(self.varz.replace_scalar('${obj.b[0]}-${obj.b[1]}'), '1-2')
        assert_equal(self.varz.replace_scalar('${dic["a"]}'), 1)
        assert_equal(self.varz.replace_scalar('${dic["o"]}'), obj)
        assert_equal(self.varz.replace_scalar('-${dic["o"].b[2]}-'), '-3-')

    def test_space_is_not_ignored_after_newline_in_extend_variable_syntax(self):
        self.varz['${x}'] = 'test string'
        self.varz['${lf}'] = '\\n'
        self.varz['${lfs}'] = '\\n '
        for inp, exp in [('${x.replace(" ", """\\n""")}', 'test\nstring'),
                         ('${x.replace(" ", """\\n """)}', 'test\n string'),
                         ('${x.replace(" ", """${lf}""")}', 'test\nstring'),
                         ('${x.replace(" ", """${lfs}""")}', 'test\n string')]:
            assert_equal(self.varz.replace_scalar(inp), exp)

    def test_escaping_with_extended_variable_syntax(self):
        self.varz['${p}'] = 'c:\\temp'
        assert self.varz['${p}'] == 'c:\\temp'
        assert_equal(self.varz.replace_scalar('${p + "\\\\foo.txt"}'),
                     'c:\\temp\\foo.txt')

    def test_internal_variables(self):
        # Internal variables are variables like ${my${name}}
        self.varz['${name}'] = 'name'
        self.varz['${my name}'] = 'value'
        assert_equal(self.varz.replace_scalar('${my${name}}'), 'value')
        self.varz['${whos name}'] = 'my'
        assert_equal(self.varz.replace_scalar('${${whos name} ${name}}'), 'value')
        assert_equal(self.varz.replace_scalar('${${whos${name}}${name}}'), 'value')
        self.varz['${my name}'] = [1, 2, 3]
        assert_equal(self.varz.replace_scalar('${${whos${name}}${name}}'), [1, 2, 3])
        assert_equal(self.varz.replace_scalar('- ${${whos${name}}${name}} -'), '- [1, 2, 3] -')

    def test_math_with_internal_vars(self):
        assert_equal(self.varz.replace_scalar('${${1}+${2}}'), 3)
        assert_equal(self.varz.replace_scalar('${${1}-${2}}'), -1)
        assert_equal(self.varz.replace_scalar('${${1}*${2}}'), 2)
        assert_equal(self.varz.replace_scalar('${${1}//${2}}'), 0)

    def test_math_with_internal_vars_with_spaces(self):
        assert_equal(self.varz.replace_scalar('${${1} + ${2.5}}'), 3.5)
        assert_equal(self.varz.replace_scalar('${${1} - ${2} + 1}'), 0)
        assert_equal(self.varz.replace_scalar('${${1} * ${2} - 1}'), 1)
        assert_equal(self.varz.replace_scalar('${${1} / ${2.0}}'), 0.5)

    def test_math_with_internal_vars_does_not_work_if_first_var_is_float(self):
        assert_raises(VariableError, self.varz.replace_scalar, '${${1.1}+${2}}')
        assert_raises(VariableError, self.varz.replace_scalar, '${${1.1} - ${2}}')
        assert_raises(VariableError, self.varz.replace_scalar, '${${1.1} * ${2}}')
        assert_raises(VariableError, self.varz.replace_scalar, '${${1.1}/${2}}')

    def test_list_variable_as_scalar(self):
        self.varz['@{name}'] = exp = ['spam', 'eggs']
        assert_equal(self.varz.replace_scalar('${name}'), exp)
        assert_equal(self.varz.replace_list(['${name}', 42]), [exp, 42])
        assert_equal(self.varz.replace_string('${name}'), str(exp))

    def test_copy(self):
        varz = Variables()
        varz['${foo}'] = 'bar'
        copy = varz.copy()
        assert_equal(copy['${foo}'], 'bar')

    def test_ignore_error(self):
        v = Variables()
        v['${X}'] = 'x'
        v['@{Y}'] = [1, 2, 3]
        for item in ['${foo}', 'foo${bar}', '${foo}', '@{zap}', '${Y}[7]',
                     '${inv', '${{inv}', '${var}[inv', '${var}[key][inv']:
            x_at_end = 'x' if (item.count('{') == item.count('}') and
                               item.count('[') == item.count(']')) else '${x}'
            assert_equal(v.replace_string(item, ignore_errors=True), item)
            assert_equal(v.replace_string('${x}'+item+'${x}', ignore_errors=True),
                         'x' + item + x_at_end)
            assert_equal(v.replace_scalar(item, ignore_errors=True), item)
            assert_equal(v.replace_scalar('${x}'+item+'${x}', ignore_errors=True),
                         'x' + item + x_at_end)
            assert_equal(v.replace_list([item], ignore_errors=True), [item])
            assert_equal(v.replace_list(['${X}', item, '@{Y}'], ignore_errors=True),
                         ['x', item, 1, 2, 3])
            assert_equal(v.replace_list(['${x}'+item+'${x}', '@{NON}'], ignore_errors=True),
                         ['x' + item + x_at_end, '@{NON}'])

    def test_sequence_subscript(self):
        sequences = (
            [42, 'my', 'name'],
            (42, ['foo', 'bar'], 'name'),
            'abcDEF123#@$',
            b'abcDEF123#@$',
            bytearray(b'abcDEF123#@$'),
        )
        for var in sequences:
            self.varz['${var}'] = var
            assert_equal(self.varz.replace_scalar('${var}[0]'), var[0])
            assert_equal(self.varz.replace_scalar('${var}[-2]'), var[-2])
            assert_equal(self.varz.replace_scalar('${var}[::2]'), var[::2])
            assert_equal(self.varz.replace_scalar('${var}[1::2]'), var[1::2])
            assert_equal(self.varz.replace_scalar('${var}[1:-3:2]'), var[1:-3:2])
            assert_raises(VariableError, self.varz.replace_scalar, '${var}[0][1]')

    def test_dict_subscript(self):
        a_key = (42, b'key')
        var = {'foo': 'bar', 42: [4, 2], 'name': b'my-name', a_key: {4: 2}}
        self.varz['${a_key}'] = a_key
        self.varz['${var}'] = var
        assert_equal(self.varz.replace_scalar('${var}[foo][-1]'), var['foo'][-1])
        assert_equal(self.varz.replace_scalar('${var}[${42}][-1]'), var[42][-1])
        assert_equal(self.varz.replace_scalar('${var}[name][:3]'), var['name'][:3])
        assert_equal(self.varz.replace_scalar('${var}[${a_key}][${4}]'), var[a_key][4])
        assert_raises(VariableError, self.varz.replace_scalar, '${var}[1]')
        assert_raises(VariableError, self.varz.replace_scalar, '${var}[42:]')
        assert_raises(VariableError, self.varz.replace_scalar, '${var}[nonex]')

    def test_custom_class_subscriptable_like_sequence(self):
        # the two class attributes are accessible via indices 0 and 1
        # slicing should be supported here as well
        bytes_key = b'my'
        var = PythonObject([1, 2, 3, 4, 5], {bytes_key: 'myname'})
        self.varz['${bytes_key}'] = bytes_key
        self.varz['${var}'] = var
        assert_equal(self.varz.replace_scalar('${var}[${0}][2::2]'), [3, 5])
        assert_equal(self.varz.replace_scalar('${var}[0][2::2]'), [3, 5])
        assert_equal(self.varz.replace_scalar('${var}[1][${bytes_key}][2:]'), 'name')
        assert_equal(self.varz.replace_scalar('${var}\\[1]'), str(var) + '[1]')
        assert_equal(self.varz.replace_scalar('${var}[:][0][4]'), var[:][0][4])
        assert_equal(self.varz.replace_scalar('${var}[:-2]'), var[:-2])
        assert_equal(self.varz.replace_scalar('${var}[:7:-2]'), var[:7:-2])
        assert_equal(self.varz.replace_scalar('${var}[2::]'), ())
        assert_raises(VariableError, self.varz.replace_scalar, '${var}[${2}]')
        assert_raises(VariableError, self.varz.replace_scalar, '${var}[${bytes_key}]')

    def test_non_subscriptable(self):
        assert_raises(VariableError, self.varz.replace_scalar, '${1}[1]')


if __name__ == '__main__':
    unittest.main()
