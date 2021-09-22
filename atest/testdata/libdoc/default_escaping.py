"""Library to document and test correct default value escaping."""
from robot.libraries.BuiltIn import BuiltIn

b = BuiltIn()


def verify_backslash(current='c:\\windows\\system', expected='c:\\windows\\system'):
    b.should_be_equal(current, expected)


def verify_internalvariables(current='first ${sca${lar}}  @{list}[${4}]  &{dict.key}[2] some env %{${somename}} and a \\${backslash}[${key}]   ',
                             expected='first ${sca${lar}}  @{list}[${4}]  &{dict.key}[2] some env %{${somename}} and a \\${backslash}[${key}]   '):
    b.should_be_equal(current, expected)


def verify_line_break(current='Hello\n World!\r\n End...\\n', expected='Hello\n World!\r\n End...\\n'):
    b.should_be_equal(current, expected)


def verify_line_tab(current='Hello\tWorld!\t\t End\\t...', expected='Hello\tWorld!\t\t End\\t...'):
    b.should_be_equal(current, expected)


def verify_spaces(current='    Hello\tW   orld!\t  \t En d\\t... ', expected='    Hello\tW   orld!\t  \t En d\\t... '):
    b.should_be_equal(current, expected)


def verify_variables(current='first ${scalar} then @{list} and &{dict.key}[2] some env %{username} and a \\${backslash}   ',
                     expected='first ${scalar} then @{list} and &{dict.key}[2] some env %{username} and a \\${backslash}   '):
    b.should_be_equal(current, expected)


def verify_all(current='first ${scalar} \nthen\t @{list} and \\\\&{dict.key}[2] so   \\    me env %{username} and a \\${backslash}   ',
               expected='first ${scalar} \nthen\t @{list} and \\\\&{dict.key}[2] so   \\    me env %{username} and a \\${backslash}   '):
    b.should_be_equal(current, expected)
