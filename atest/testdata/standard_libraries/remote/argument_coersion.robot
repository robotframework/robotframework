*** Settings ***
Test Template     Argument Should Be Passed Correctly
Library           Remote    127.0.0.1:${PORT}
Library           Helper.py
Library           Collections
Variables         variables.py

*** Variables ***
${PORT}           8270

*** Test Cases ***
String
    'Hello, world!'
    u'hyv\\xe4 \\u2603'
    '\\x7f'
    u'\\x7f\\x80\\xff'
    ''

Newline and tab
    '\\t\\n\\r'    '\\t\\n\\n'

Binary
    '\\x00\\x01\\x02'         b'\\x00\\x01\\x02'    binary=yes
    'foo\\x00bar'             b'foo\\x00bar'        binary=yes
    u'\\x00\\x01'             b'\\x00\\x01'         binary=yes
    u'\\x00\\xe4\\xff'        b'\\x00\\xe4\\xff'    binary=yes
    bytearray([0, 1, 228])    b'\\x00\\x01\\xe4'    binary=yes

Binary in non-ASCII range
    b'\\x00\\x01\\xe4'              binary=yes
    b'\\x80'                        binary=yes
    b'\\xff'                        binary=yes
    bytearray([255])    b'\\xff'    binary=yes

Binary with too big Unicode characters
    [Template]  Run Keyword And Expect Error
    ValueError: Cannot represent *'\\x00\\x01*' as binary.    One Argument    \x00\x01\u2603

Unrepresentable Unicode
    [Template]  Run Keyword And Expect Error
    *    One Argument    \uFFFF
    *    One Argument    \x00

Integer
    0
    42
    -1

Float
    0.0
    3.14
    -0.5

Boolean
    True
    False

None
    None    ''

Datetime
    datetime.datetime(2023, 9, 12, 16, 8)    datetime(2023, 9, 12, 16, 8)

Date
    datetime.date(2023, 9, 12)               datetime(2023, 9, 12)

Timedelta
    datetime.timedelta(seconds=3.14)         3.14

Custom object
    [Documentation]    Arbitrary objects cannot be transferred over XML-RPC and thus only their string presentation is used
    MyObject()    '<MyObject>'
    MyObject('xxx')    'xxx'

Custom object with non-ASCII representation
    MyObject(u'hyv\\xe4')    u'hyv\\xe4'

Custom object with binary representation
    MyObject('\\x00\\x01')    b'\\x00\\x01'    binary=yes

List
    \[]
    \['a', 'b', 'c']
    \['\\x7f', u'\\x7f']

List with non-string values
    \[1, 2, None, (), {'a': 1}]    [1, 2, '', [], {'a': 1}]

List with non-ASCII values
    \[u'\\xe4', u'\\u2603']

List with non-ASCII byte values
    \[b'\\x80', b'\\xe4']    binary=yes

List with binary values
    \['\\x00', u'\\x01']    \[b'\\x00', b'\\x01']    binary=yes

Nested list
    \[['a', 'b'], 3, [[[4], True]]]

List-like
    ()    []
    ('a', 'b', 'c')    ['a', 'b', 'c']
    ('One', -2, False, (None,), u'\\xe4')    ['One', -2, False, [''], u'\\xe4']
    set()    []
    list(i for i in range(5))    [0, 1, 2, 3, 4]

Dictionary
    {}
    {'one': '1', 'spam': 'eggs'}
    {'\\x7f': '\\x7f'}

Dictionary with non-string keys and values
    {1: 'a', 2: 3, (): (), None: None}    {'1': 'a', '2': 3, '()': [], '': ''}

Dictionary with non-ASCII keys
    {u'\\xe4': 1}
    {u'\\u2603': 2}

Dictionary with non-ASCII values
    {'1': u'\\xe4'}
    {'2': u'\\u2603'}

Dictionary with non-ASCII byte keys
    {b'\\x80': 'xx'}    {'\\\\x80': 'xx'}

Dictionary with non-ASCII byte values
    {'xx': b'\\xe4'}    binary=yes

Dictionary with binary keys is not supported
    [Documentation]    FAIL ValueError: Dictionary keys cannot be binary. Got b'\\x00'.
    {'\\x00': 'value'}

Dictionary with binary values
    {0: '\\x00', 1: u'\\x01'}    {'0': b'\\x00', '1': b'\\x01'}    binary=yes

Nested dictionary
    {'a': 0, 'b': True, 'c': {'x': [1, 2, 3]}, '\\x7f': '\\x7f'}

Mapping
    MyMapping()    {}
    MyMapping(a=1, b='\\x01')    {'a': 1, 'b': b'\\x01'}
    MyMapping(a='one', b=2, c=[None, True])    {'a': 'one', 'b': 2, 'c': ['', True]}

*** Keywords ***
Argument Should Be Passed Correctly
    [Arguments]    ${argument}    ${expected}=${NONE}    ${binary}=${FALSE}
    ${expected} =    Get Non None    ${expected}    ${argument}
    ${ns} =    Create Dictionary    MyObject=${MyObject}    MyMapping=${MyMapping}
    ${argument} =    Evaluate    ${argument}    namespace=${ns}
    Argument Should Be    ${argument}    ${expected}    ${binary}
    Kwarg Should Be    argument=${argument}    expected=${expected}    binary=${binary}
