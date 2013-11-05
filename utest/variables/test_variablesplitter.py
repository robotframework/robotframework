import unittest

from robot.variables import VariableSplitter
from robot.utils.asserts import assert_equals


class TestVariableSplitter(unittest.TestCase):
    _identifiers = ['$','@','%','&','*']

    def test_empty(self):
        self._test('')
        self._test('                                       ')

    def test_no_vars(self):
        for inp in ['hello world', '$hello', '{hello}', '$\\{hello}',
                    '${hello', '$hello}', 'a bit longer sting here']:
            self._test(inp)

    def test_backslashes(self):
        for inp in ['\\', '\\\\', '\\\\\\\\\\', '\\hello\\\\world\\\\\\']:
            self._test(inp)

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

    def test_escape_internal_closing_curly(self):
        self._test(r'${embed:\d{2\}}', '${embed:\d{2\}}')
        self._test(r'{}{${e:\d\{4\}-\d{2\}-\d{2\}}}}',
                   '${e:\d\{4\}-\d{2\}-\d{2\}}', start=3)
        self._test(r'$&{\{\}{\}\\}{}', r'&{\{\}{\}\\}', start=1)
        self._test(r'${&{\}{\\\\}\\}}{}', r'${&{\}{\\\\}\\}', internal=True)

    def test_no_unescaped_internal_closing_curly(self):
        self._test(r'${x\}')
        self._test(r'${x\\\}')
        self._test(r'${x\\\\\\\}')

    def test_uneven_curlys(self):
        self._test('${x:{}', '${x:{}')
        self._test('${x:{{}}', '${x:{{}')
        self._test('xx${x:{}xx', '${x:{}', start=2)
        self._test('{%{{}{{}}{{', '%{{}', start=1)

    def test_multiple_vars(self):
        self._test('${hello} ${world}', '${hello}', 0)
        self._test('hi %{u}2 and @{u2} and also *{us3}', '%{u}', 3)
        self._test('0123456789 %{1} and @{2', '%{1}', 11)

    def test_escaped_var(self):
        self._test('\\${hello}')
        self._test('hi \\\\\\${hello} moi')

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
            self._test(inp, var, start, internal=var.count('{') > 1)

    def test_index(self):
        self._test('@{x}[0]', '@{x}', index='0')
        self._test('.@{x}[42]..', '@{x}', start=1, index='42')
        self._test('@{x}[]', '@{x}', index='')
        self._test('@{x}[inv]', '@{x}', index='inv')
        self._test('@{x}[0', '@{x}')
        self._test('@{x}}[0]', '@{x}')
        self._test('${x}[0]', '${x}')
        self._test('%{x}[0]', '%{x}')
        self._test('*{x}[0]', '*{x}')
        self._test('&{x}[0]', '&{x}')

    def test_index_with_iternal_vars(self):
        self._test('@{x}[${i}]', '@{x}', index='${i}')
        self._test('xx @{x}[${i}] ${xyz}', '@{x}', start=3, index='${i}')
        self._test('@@@@@{X{X}[${${i}-${${${i}}}}]', '@{X{X}', start=4,
                   index='${${i}-${${${i}}}}')
        self._test('@{${i}}[${j{}]', '@{${i}}', index='${j{}', internal=True)

    def test_custom_identifiers(self):
        for inp, start in [('@{x}${y}', 4),
                           ('%{x} ${y}', 5),
                           ('*{x}567890${y}', 10),
                           ('&{x}%{x}@{x}\\${x}${y}',
                            len('&{x}%{x}@{x}\\${x}'))]:
            self._test(inp, '${y}', start, identifiers=['$'])

    def test_identifier_as_variable_name(self):
        for i in self._identifiers:
            for count in 1, 2, 3, 42:
                var = '%s{%s}' % (i, i*count)
                self._test(var, var)
                self._test(var+'spam', var)
                self._test('eggs'+var+'spam', var, start=4)
                self._test(i+var+i, var, start=1)

    def test_identifier_as_variable_name_with_internal_vars(self):
        for i in self._identifiers:
            for count in 1, 2, 3, 42:
                var = '%s{%s{%s}}' % (i, i*count, i)
                self._test(var, var, internal=True)
                self._test('eggs'+var+'spam', var, start=4, internal=True)
                var = '%s{%s{%s}}' % (i, i*count, i*count)
                self._test(var, var, internal=True)
                self._test('eggs'+var+'spam', var, start=4, internal=True)

    def test_many_possible_starts_and_ends(self):
        self._test('{}'*10000)
        self._test('{{}}'*1000 + '${var}', '${var}', start=4000)

    def _test(self, inp, variable=None, start=0, index=None,
              identifiers=_identifiers, internal=False):
        if variable is None:
            identifier = base = None
            start = end = -1
        else:
            identifier = variable[0]
            base = variable[2:-1]
            end = start + len(variable)
            if index is not None:
                end += len(index) + 2
        res = VariableSplitter(inp, identifiers)
        assert_equals(res.base, base, "'%s' base" % inp)
        assert_equals(res.start, start, "'%s' start" % inp)
        assert_equals(res.end, end, "'%s' end" % inp)
        assert_equals(res.identifier, identifier, "'%s' indentifier" % inp)
        assert_equals(res.index, index, "'%s' index" % inp)
        assert_equals(res._may_have_internal_variables, internal,
                      "'%s' internal" % inp)


if __name__ == '__main__':
    unittest.main()
