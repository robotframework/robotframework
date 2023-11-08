import unittest

from robot.errors import DataError
from robot.utils.asserts import (assert_equal, assert_false,
                                 assert_raises_with_msg, assert_true)
from robot.variables.search import (search_variable, unescape_variable_syntax,
                                    VariableMatches)


class TestSearchVariable(unittest.TestCase):
    _identifiers = ['$', '@', '%', '&', '*']

    def test_empty(self):
        self._test('')
        self._test('                                       ')

    def test_no_vars(self):
        for inp in ['hello world', '$hello', '{hello}', r'$\{hello}',
                    '$h{ello}', 'a bit longer sting here']:
            self._test(inp)

    def test_not_string(self):
        self._test(42)
        self._test([1, 2, 3])

    def test_backslashes(self):
        for inp in ['\\', '\\\\', '\\\\\\\\\\', '\\hello\\\\world\\\\\\']:
            self._test(inp)

    def test_one_var(self):
        self._test('${hello}', '${hello}')
        self._test('1 @{hello} more', '@{hello}', start=2)
        self._test('*{hi}}', '*{hi}')
        self._test('{%{{hi}}', '%{{hi}}', start=1)
        self._test('-= ${} =-', '${}', start=3)

    def test_escape_internal_curlys(self):
        self._test(r'${embed:\d\{2\}}', r'${embed:\d\{2\}}')
        self._test(r'{}{${e:\d\{4\}-\d\{2\}-\d\{2\}}}}',
                   r'${e:\d\{4\}-\d\{2\}-\d\{2\}}', start=3)
        self._test(r'$&{\{\}\{\}\\}{}', r'&{\{\}\{\}\\}', start=1)
        self._test(r'${&{\}\{\\\\}\\}}{}', r'${&{\}\{\\\\}\\}')

    def test_matching_internal_curlys_dont_need_to_be_escaped(self):
        self._test(r'${embed:\d{2}}', r'${embed:\d{2}}')
        self._test(r'{}{${e:\d{4}-\d{2}-\d{2}}}}',
                   r'${e:\d{4}-\d{2}-\d{2}}', start=3)
        self._test(r'$&{{}{}\\}{}', r'&{{}{}\\}', start=1)
        self._test(r'${&{{\\\\}\\}}{}}', r'${&{{\\\\}\\}}')

    def test_uneven_curlys(self):
        for inp in ['${x', '${x:{}', '${y:{{}}', 'xx${z:{}xx', '{${{}{{}}{{',
                    r'${x\}', r'${x\\\}', r'${x\\\\\\\}']:
            for identifier in '$@&%':
                variable = identifier + inp.split('$')[1]
                assert_raises_with_msg(
                    DataError,
                    f"Variable '{variable}' was not closed properly.",
                    search_variable, inp.replace('$', identifier)
                )
                self._test(inp.replace('$', identifier), ignore_errors=True)
        self._test('}{${xx:{}}}}}', '${xx:{}}', start=2)

    def test_escaped_uneven_curlys(self):
        self._test(r'${x:\{}', r'${x:\{}')
        self._test(r'${y:{\{}}', r'${y:{\{}}')
        self._test(r'xx${z:\{}xx', r'${z:\{}', start=2)
        self._test(r'{%{{}\{{}}{{', r'%{{}\{{}}', start=1)
        self._test(r'${xx:{}\}\}\}}', r'${xx:{}\}\}\}}')

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
                ('\\${esc}\\\\${not}${n2}', '${not}', len('\\${esc}\\\\'))]:
            self._test(inp, var, start)

    def test_internal_vars(self):
        for inp, var, start in [
                ('${hello${hi}}', '${hello${hi}}', 0),
                ('bef ${${hi}hello} aft', '${${hi}hello}', 4),
                (r'\${not} ${hel${hi}lo} ', '${hel${hi}lo}', len(r'\${not} ')),
                ('${${hi}${hi}}\\', '${${hi}${hi}}', 0),
                ('${${hi${hi}}} ${xx}', '${${hi${hi}}}', 0),
                (r'${\${hi${hi}}}', r'${\${hi${hi}}}', 0),
                (r'\${${hi${hi}}}', '${hi${hi}}', len(r'\${')),
                (r'\${\${hi\\${h${i}}}}', '${h${i}}', len(r'\${\${hi\\'))]:
            self._test(inp, var, start)

    def test_incomplete_internal_vars(self):
        for inp in ['${var$', '${var${', '${var${int}']:
            for identifier in '$@&%':
                variable = inp.replace('$', identifier)
                assert_raises_with_msg(
                    DataError,
                    f"Variable '{variable}' was not closed properly.",
                    search_variable, variable
                )
                self._test(variable, ignore_errors=True)
        self._test('}{${xx:{}}}}}', '${xx:{}}', start=2)

    def test_item_access(self):
        self._test('${x}[0]', '${x}', items='0')
        self._test('.${x}[key]..', '${x}', start=1, items='key')
        self._test('${x}[]', '${x}', items='')
        self._test('${x}}[0]', '${x}')

    def test_nested_item_access(self):
        self._test('${x}[0][1]', '${x}', items=['0', '1'])
        self._test('xx${x}[key][42][-1][xxx]', '${x}', start=2,
                   items=['key', '42', '-1', 'xxx'])

    def test_item_access_with_vars(self):
        self._test('${x}[${i}]', '${x}', items='${i}')
        self._test('xx ${x}[${i}] ${xyz}', '${x}', start=3, items='${i}')
        self._test('$$$$${XX}[${${i}-${${${i}}}}]', '${XX}', start=4,
                   items='${${i}-${${${i}}}}')
        self._test('${${i}}[${j{}}]', '${${i}}', items='${j{}}')
        self._test('${x}[${i}][${k}]', '${x}', items=['${i}', '${k}'])

    def test_item_access_with_escaped_squares(self):
        self._test(r'${x}[\]]', '${x}', items=r'\]')
        self._test(r'${x}[\\]]', '${x}', items=r'\\')
        self._test(r'${x}[\[]', '${x}', items=r'\[')
        self._test(r'${x}\[k]', '${x}')
        self._test(r'${x}\[k', '${x}')
        self._test(r'${x}[k]\[i]', '${x}', items='k')

    def test_item_access_with_matching_squares(self):
        self._test('${x}[[]]', '${x}', items=['[]'])
        self._test('${x}[${y}[0][key]]', '${x}', items=['${y}[0][key]'])
        self._test('${x}[${y}[0]][key]', '${x}', items=['${y}[0]', 'key'])

    def test_unclosed_item(self):
        for inp in ['${x}[0', '${x}[0][key', r'${x}[0\]']:
            msg = f"Variable item '{inp}' was not closed properly."
            assert_raises_with_msg(DataError, msg, search_variable, inp)
            self._test(inp, ignore_errors=True)
        self._test('[${var}[i]][', '${var}', start=1, items='i')

    def test_nested_list_and_dict_item_syntax(self):
        self._test('@{x}[0]', '@{x}', items='0')
        self._test('&{x}[key]', '&{x}', items='key')

    def test_escape_item(self):
        self._test('${x}\\[0]', '${x}')
        self._test('@{x}\\[0]', '@{x}')
        self._test('&{x}\\[key]', '&{x}')

    def test_no_item_with_others_vars(self):
        self._test('%{x}[0]', '%{x}')
        self._test('*{x}[0]', '*{x}')

    def test_custom_identifiers(self):
        for inp, start in [('@{x}${y}', 4),
                           ('%{x} ${y}', 5),
                           ('*{x}567890${y}', 10),
                           (r'&{x}%{x}@{x}\${x}${y}',
                            len(r'&{x}%{x}@{x}\${x}'))]:
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
                self._test(var, var)
                self._test('eggs'+var+'spam', var, start=4)
                var = '%s{%s{%s}}' % (i, i*count, i*count)
                self._test(var, var)
                self._test('eggs'+var+'spam', var, start=4)

    def test_many_possible_starts_and_ends(self):
        self._test('{}'*10000)
        self._test('{{}}'*1000 + '${var}', '${var}', start=4000)
        self._test('${var}' + '[i]'*1000, '${var}', items=['i']*1000)

    def test_complex(self):
        self._test('${${PER}SON${2}[${i}]}', '${${PER}SON${2}[${i}]}')
        self._test('${x}[${${PER}SON${2}[${i}]}]', '${x}',
                   items='${${PER}SON${2}[${i}]}')

    def _test(self, inp, variable=None, start=0, items=None,
              identifiers=_identifiers, ignore_errors=False):
        if isinstance(items, str):
            items = (items,)
        elif items is None:
            items = ()
        else:
            items = tuple(items)
        if variable is None or ignore_errors:
            identifier = base = None
            start = end = -1
            is_var = is_scal_var = is_list_var = is_dict_var = False
        else:
            identifier = variable[0]
            base = variable[2:-1]
            end = start + len(variable)
            is_var = inp == variable
            if items:
                items_str = ''.join(f'[{i}]' for i in items)
                end += len(items_str)
                is_var = inp == f'{variable}{items_str}'
            is_list_var = is_var and inp[0] == '@'
            is_dict_var = is_var and inp[0] == '&'
            is_scal_var = is_var and inp[0] == '$'
        match = search_variable(inp, identifiers, ignore_errors)
        assert_equal(match.base, base, f'{inp!r} base')
        assert_equal(match.start, start, f'{inp!r} start')
        assert_equal(match.end, end, f'{inp!r} end')
        assert_equal(match.before, inp[:start] if start != -1 else inp)
        assert_equal(match.match, inp[start:end] if end != -1 else None)
        assert_equal(match.after, inp[end:] if end != -1 else '')
        assert_equal(match.identifier, identifier, f'{inp!r} identifier')
        assert_equal(match.items, items, f'{inp!r} item')
        assert_equal(match.is_variable(), is_var)
        assert_equal(match.is_scalar_variable(), is_scal_var)
        assert_equal(match.is_list_variable(), is_list_var)
        assert_equal(match.is_dict_variable(), is_dict_var)

    def test_is_variable(self):
        for no in ['', 'xxx', '${var} not alone', r'\${notvar}', r'\\${var}',
                   '${var}xx}', '${x}${y}']:
            assert_false(search_variable(no).is_variable(), no)
        for yes in ['${var}', r'${var$\{}', '${var${internal}}', '@{var}',
                    '@{var}[0]']:
            assert_true(search_variable(yes).is_variable(), yes)

    def test_is_list_variable(self):
        for no in ['', 'xxx', '@{var} not alone', r'\@{notvar}', r'\\@{var}',
                   '@{var}xx}', '@{x}@{y}', '${scalar}', '&{dict}']:
            assert_false(search_variable(no).is_list_variable())
        assert_true(search_variable('@{list}').is_list_variable())
        assert_true(search_variable('@{x}[0]').is_list_variable())
        assert_true(search_variable('@{grandpa}[mother][child]').is_list_variable())

    def test_is_dict_variable(self):
        for no in ['', 'xxx', '&{var} not alone', r'\@{notvar}', r'\\&{var}',
                   '&{var}xx}', '&{x}&{y}', '${scalar}', '@{list}']:
            assert_false(search_variable(no).is_dict_variable())
        assert_true(search_variable('&{dict}').is_dict_variable())
        assert_true(search_variable('&{yzy}[afa]').is_dict_variable())
        assert_true(search_variable('&{x}[k][foo][bar][1]').is_dict_variable())


class TestVariableMatches(unittest.TestCase):

    def test_no_variables(self):
        matches = VariableMatches('no vars here', identifiers='$')
        assert_equal(list(matches), [])
        assert_equal(bool(matches), False)
        assert_equal(len(matches), 0)

    def test_one_variable(self):
        matches = VariableMatches('one ${var} here', identifiers='$')
        assert_equal(bool(matches), True)
        assert_equal(len(matches), 1)
        self._assert_match(next(iter(matches)), 'one ', '${var}', ' here')

    def test_multiple_variables(self):
        matches = VariableMatches('${1} @{2} and %{3}', identifiers='$@%')
        assert_equal(bool(matches), True)
        assert_equal(len(matches), 3)
        m1, m2, m3 = matches
        self._assert_match(m1, '', '${1}', ' @{2} and %{3}')
        self._assert_match(m2, ' ', '@{2}', ' and %{3}')
        self._assert_match(m3, ' and ', '%{3}', '')

    def test_can_be_iterated_many_times(self):
        matches = VariableMatches('one ${var} here', identifiers='$')
        assert_equal(bool(matches), True)
        assert_equal(bool(matches), True)
        assert_equal(len(matches), 1)
        assert_equal(len(matches), 1)
        self._assert_match(list(matches)[0], 'one ', '${var}', ' here')
        self._assert_match(list(matches)[0], 'one ', '${var}', ' here')

    def _assert_match(self, match, before, variable, after):
        assert_equal(match.before, before)
        assert_equal(match.match, variable)
        assert_equal(match.after, after)


class TestUnescapeVariableSyntax(unittest.TestCase):

    def test_no_backslash(self):
        for inp in ['no escapes', '']:
            self._test(inp)

    def test_no_variable(self):
        for inp in ['\\', r'\n', r'\d+', '☃', r'\$', r'\@', r'\&']:
            self._test(inp)
            self._test(f'Hello, {inp}!')

    def test_unescape_variable(self):
        for i in '$@&%':
            self._test(r'\%s{var}' % i, '%s{var}' % i)
            self._test(r'=\%s{var}=' % i, '=%s{var}=' % i)
            self._test(r'\\%s{var}' % i)
            self._test(r'\\\%s{var}' % i, r'\\%s{var}' % i)
            self._test(r'\\\\%s{var}' % i)
        self._test(r'\${1} \@{2} \&{3} \%{4}', '${1} @{2} &{3} %{4}')

    def test_unescape_curlies(self):
        self._test(r'\{', '{')
        self._test(r'\}', '}')
        self._test(r'=\}=\{=', '=}={=')
        self._test(r'=\\}=\\{=')
        self._test(r'=\\\}=\\\{=', r'=\\}=\\{=')
        self._test(r'=\\\\}=\\\\{=')

    def test_misc(self):
        self._test(r'$\{foo\}', '${foo}')
        self._test(r'\$\{foo\}', r'\${foo}')
        self._test(r'\${\n}', r'${\n}')
        self._test(r'\${\${x}}', r'${${x}}')
        self._test(r'\${foo', r'\${foo')

    def _test(self, inp, exp=None):
        if exp is None:
            exp = inp
        assert_equal(unescape_variable_syntax(inp), exp)


if __name__ == '__main__':
    unittest.main()
