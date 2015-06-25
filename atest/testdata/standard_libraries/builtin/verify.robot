*** Settings ***
Variables         variables_to_verify.py

*** Variables ***
${STR0}           0
${STR1}           1
${INT0}           ${0}
${INT1}           ${1}
@{LIST}           a    b    cee    b    ${42}
${LONG}           This is a bit longer sentence and it even has a friend here.
...               This is the friend of the previous sentence and it is also
...               quite long, actually even longer than its friend.


*** Test Cases ***
Should Not Be True
    [Documentation]    FAIL '0 < 1' should not be true.
    Should Not Be True    0 > 1
    ${empty list} =    Create List
    Should Not Be True    ${empty list}
    Should Not Be True    ${INT0} < ${INT1}

Should Not Be True With Message
    [Documentation]    FAIL My message
    Should Not Be True    True    My message

Should Not Be True With Invalid Expression
    [Documentation]    FAIL STARTS: Evaluating expression 'this is invalid' failed: NameError:
    Should Not Be True    this is invalid

Should Be True
    [Documentation]    FAIL '1 != 1 and True or False' should be true.
    Should Be True    -1 <= ${STR1} <= 1
    Should Be True    -${STR1} < ${STR0} < ${STR1}
    ${list} =    Create List    0
    Should Be True    ${list}
    Should Be True    1 != 1 and True or False

Should Be True With Message
    [Documentation]    FAIL My error message
    Should Be True    False    My error message

Should Be True With Invalid Expression
    [Documentation]    FAIL STARTS: Evaluating expression '"quotes" != "quote missing' failed: SyntaxError:
    Should Be True    "quotes" != "quote missing

Should (Not) Be True is evaluated with os- and sys-modules
    Should Be True    os.sep
    Should Be True    sys.platform
    Should Not Be True    'os.sep' == 'wrong'
    Should Not Be True    'sys.platform' == 'hurd'    # let's see when this starts failing

Should (Not) Be True is evaluated with robot's variables
    ${lst} =    Create list   foo    bar
    Should Be True    lst[0] == 'foo'
    Should Not Be True   len(lst) == 3

Should Not Be Equal
    [Documentation]    FAIL 1 == 1
    [Template]    Should Not Be Equal
    ${STR1}    Not ${STR1}
    ${STR1}    ${INT1}
    ${STR1}    1

Should Not Be Equal with bytes containing non-ascii characters
    [Documentation]    FAIL ${BYTES WITH NON ASCII} == ${BYTES WITH NON ASCII}
    Should Not Be Equal    ${BYTES WITH NON ASCII}    ${BYTES WITHOUT NON ASCII}
    Should Not Be Equal    ${BYTES WITH NON ASCII}    unicode
    Should Not Be Equal    ${BYTES WITH NON ASCII}    ${BYTES WITH NON ASCII}

Should Be Equal
    [Documentation]    FAIL Error message: A != B
    [Template]    Should Be Equal
    ${STR1}    1
    ${INT1}    ${1}
    ${BYTES WITHOUT NON ASCII}    ${BYTES WITHOUT NON ASCII}
    A    B    Error message    values=yes

Should Be Equal fails with values
    [Documentation]    FAIL Several failures occurred:\n\n 1) 3: 1 != 2\n\n 2) c: a != b\n\n 3) z: x != y
    [Template]    Should Be Equal
    1    2    3
    a    b    c    values=true
    x    y    z    values=${42}

Should Be Equal fails without values
    [Documentation]    FAIL Several failures occurred:\n\n 1) 3\n\n 2) c\n\n 3) z\n\n 4) -
    [Template]    Should Be Equal
    1    2    3    values=FALSE
    a    b    c    No Values
    x    y    z    values=no
    .    ,    -    ${NONE}

Should Be Equal with bytes containing non-ascii characters
    [Documentation]    FAIL ${BYTES WITH NON ASCII} != ${BYTES WITHOUT NON ASCII}
    Should be equal    ${BYTES WITH NON ASCII}    ${BYTES WITH NON ASCII}
    Should be equal    ${BYTES WITH NON ASCII}    ${BYTES WITHOUT NON ASCII}

Should Be Equal with unicode and bytes with non-ascii characters
    [Documentation]    FAIL ${BYTES WITH NON ASCII} != this fails
    Should be equal    ${BYTES WITHOUT NON ASCII}    hyva
    Should be equal    ${BYTES WITH NON ASCII}    this fails

Should Be Equal When Types Differ But String Representations Are Same
    [Documentation]    FAIL 1 (string) != 1 (integer)
    Should Be Equal    ${STR1}    ${INT1}

Should Not Be Equal As Integers
    [Documentation]    FAIL This message only
    [Template]    Should Not Be Equal As Integers
    1    ${STR0}
    0    ${INT1}
    1    ${INT1}    This message only    No values

Should Not Be Equal As Integers With Base
    [Documentation]    Conversion functionality tested with `Convert To Integer`
    [Template]    Should Not Be Equal As Integers
    ABC    DEF    base=16
    0b10    10
    0x10    0o10

Should Be Equal As Integers
    [Documentation]    FAIL -1 != 1
    [Template]    Should Be Equal As Integers
    ${STR1}${STR0}${STR0}    ${STR1}${STR0}${STR0}
    ${STR1}${STR0}${STR0}    ${100.0}
    -${STR1}    ${STR1}

Should Be Equal As Integers With Base
    [Documentation]    Conversion functionality tested with `Convert To Integer`
    [Template]    Should Be Equal As Integers
    ABCD    abcd    base=16
    0b10    2
    0xFF    0o377
    0b0    0
    0x0    0o0
    0b1    1
    0x1    0o1

Should Not Be Equal As Numbers
    [Documentation]    FAIL Fails again: 1.1 == 1.1
    [Template]    Should Not Be Equal As Numbers
    ${STR1}.${STR1}    1.2
    ${STR1}.${STR1}    ${1.2}
    ${STR1}.${STR1}    1.1    Fails again

Should Not Be Equal As Numbers With Precision
    [Documentation]    FAIL Failing: 1.0 == 1.0
    [Template]    Should Not Be Equal As Numbers
    1.123    1.456    precision=1
    1.123    ${1.1}    precision=2
    ${1.123}    ${1.12}    precision=3
    1123    1456    precision=-2
    112    145    precision=-1
    1.12    1.45    Failing    precision=0

Should Be Equal As Numbers
    [Documentation]    FAIL Only this message
    [Template]    Should Be Equal As Numbers
    ${STR1}    ${STR1}.${STR0}${STR0}
    ${STR1}.000001    ${STR1}.${STR0}${STR0}${STR1}    Only this message    False

Should Be Equal As Numbers With Precision
    [Documentation]    FAIL Failure: 110.0 != 150.0
    [Template]    Should Be Equal As Numbers
    1.123    1.456    precision=0
    1.123    ${1.1}    precision=1
    ${1.123}    ${1.12}    precision=2
    1123    1456    precision=-3
    112    145    precision=-2
    112    145    Failure    precision=-1

Should Not Be Equal As Strings
    [Documentation]    FAIL These strings most certainly should not be equal
    [Template]    Should Not Be Equal As Strings
    1    ${1.1}
    False    ${True}
    bar    bar    These strings most certainly should not be equal    False

Should Be Equal As Strings
    [Documentation]    FAIL foo != bar
    [Template]    Should Be Equal As Strings
    ${1}    1
    ${None}    None
    foo    bar

Should Not Start With
    [Documentation]    FAIL 'Hello, world!' starts with 'Hello'
    [Template]    Should Not Start With
    Hello, world!    Hi
    Hello, world!    HELLO
    Hello, world!    Hello

Should Start With
    [Documentation]    FAIL My message: '${LONG}' does not start with 'Does not start'
    [Template]    Should Start With
    Hello, world!    Hello
    Hello, world!    Hello, world!
    ${LONG}    Does not start    My message    values=true

Should Start With without values
    [Documentation]    FAIL My message
    Should Start With    ${LONG}    Nope    My message    values=No values

Should Not End With
    [Documentation]    FAIL Message only
    [Template]    Should Not End With
    Hello!    Hello
    Hillo!    !    Message only    No Values

Should End With without values
    [Documentation]    FAIL My message
    Should End With    ${LONG}    Nope    My message    values=No values

Should End With
    [Documentation]    FAIL 'Hello, world!' does not end with '?'
    [Template]    Should End With
    Hello, world!    !
    Hello, world!    Hello, world!
    Hello, world!    ?

Should Not Contain
    [Documentation]    FAIL 'Hello yet again' contains 'yet'
    [Template]    Should Not Contain
    Hello again    yet
    Hello yet again    yet

Should Not Contain With Non-String Values
    [Documentation]    FAIL '(1, 2)' contains '1'
    ${list}    ${tuple}    ${dict} =    Evaluate    ['a'], (1,2), {'a':1, 'b':2}
    Should Not Contain    ${list}    b
    Should Not Contain    ${tuple}    ${42}
    Should Not Contain    ${dict}    c
    Should Not Contain    ${tuple}    ${1}

Should Contain
    [Documentation]    FAIL Message: 'abcdefg' does not contain 'ABCDEFG'
    [Template]    Should Contain
    abcdefg    cd
    abcdefg    abcdefg    Massage
    abcdefg    ABCDEFG    Message

Should Contain With Non-String Values
    [Documentation]    FAIL '{'a': 1}' does not contain 'c'
    ${list}    ${tuple}    ${dict} =    Evaluate    ['a'], (1,2), {'a':1}
    Should Contain    ${list}    a
    Should Contain    ${tuple}    ${2}
    Should Contain    ${dict}    a
    Should Contain    ${dict}    c

Should Not Match
    [Documentation]    FAIL 'Hello world' matches '?ello*'
    Should Not Match    this string does not    match this pattern
    Should Not Match    Case matters    case matters
    Should Not Match    Hello world    ?ello*

Should Match
    [Documentation]    FAIL Failure: 'NOK' does not match 'OK'
    Should Match    abcdefghijklmnopqrstuvwxyz    ?*?efg*p*t?vw*z
    Should Match    NOK    OK    Failure

Should Match with bytes containing non-ascii characters
    [Documentation]    FAIL '${BYTES WITH NON ASCII}' does not match 'aaappaa'
    Should match    ${BYTES WITH NON ASCII}    aaappaa

Should Not Match Regexp
    [Documentation]    FAIL 'James Bond 007' matches '^J\\w{4}\\sB[donkey]+ \\d*$'
    Should Not Match Regexp    this string does not    match this pattern
    Should Not Match Regexp    James Bond 007    ^J\\w{4}\\sB[donkey]+ \\d*$

Should Match Regexp
    [Documentation]    FAIL Something failed
    Should Match Regexp    Foo: 42    \\w+: \\d{2}
    Should Match Regexp    IGNORE CASE    (?i)case
    Should Match Regexp    ${EMPTY}    whatever    Something failed    No values

Should Match Regexp with bytes containing non-ascii characters
    [Documentation]    FAIL '${BYTES WITH NON ASCII}' does not match 'aappaa'
    Should Match Regexp    ${BYTES WITH NON ASCII}    aappaa

Should Match Regexp Returns Match And Groups
    ${ret} =    Should Match Regexp    This is a multiline\nstring!!    (?im)^STR\\w+!!
    ${match}    ${group} =    Should Match Regexp    ${ret}    ^(\\w+)!!$
    Should Be Equal    ${match}    ${ret}
    Should Be Equal    ${group}    string
    ${match}    @{groups} =    Should Match Regexp    Foo: 42 (xxx)    ^(Fo+)([:.;]) (\\d+?)
    Should Be Equal    ${match}    Foo: 4
    Should Be True    @{groups} == ['Foo', ':', '4']
    ${match}    ${group1}    ${group2} =    Should Match Regexp    Hello, (my) World!!!!!    (?ix)^hel+o,\\s # Comment \n \\((my|your)\\)\\ WORLD(!*)$
    Should Be Equal    ${match}    Hello, (my) World!!!!!
    Should Be Equal    ${group1}    my
    Should Be Equal    ${group2}    !!!!!

Get Length
    [Documentation]    FAIL Could not get length of '10'.
    Verify Get Length    ${TUPLE 0}    0
    Verify Get Length    ${LIST 1}    1
    Verify Get Length    ${DICT 2}    2
    Verify Get Length    ${CUSTOM 3}    3
    Verify Get Length    some string    11
    Verify Get Length    ${EMPTY}    0
    Verify Get Length    ${10}    Getting length from an int fails

Length Should Be
    [Documentation]    FAIL Length of '['a', 'b']' should be 3 but is 2.
    : FOR    ${input}    ${expected}    IN    ${TUPLE 0}    0    ${LIST 0}
    ...    0    ${DICT 0}    ${0}    ${EMPTY}    ${0.0}    ${TUPLE 1}
    ...    1    ${LIST 3}    3    ${DICT 3}    ${3}    ${CUSTOM 0}
    ...    0    ${CUSTOM 1}    1    123456789012345678901    ${2.1e1}
    \    Length Should Be    ${input}    ${expected}
    Length Should Be    ${LIST 2}    3

Length Should Be With Non Default Message
    [Documentation]    FAIL This fails
    Length Should Be    ${LIST 2}    2    This passes
    Length Should Be    ${LIST 2}    3    This fails

Length Should Be With Invalid Length
    [Documentation]    FAIL STARTS: 'This is not an integer' cannot be converted to an integer: ValueError:
    Length Should Be    ${LIST 2}    This is not an integer

Should Be Empty
    [Documentation]    FAIL '['a']' should be empty.
    Should Be Empty    ${TUPLE 0}
    Should Be Empty    ${LIST 0}
    Should Be Empty    ${DICT 0}
    Should Be Empty    ${CUSTOM 0}
    Should Be Empty    ${EMPTY}
    Should Be Empty    ${LIST 1}

Should Be Empty With Non Default Message
    [Documentation]    FAIL My non-default error message
    Should Be Empty    ${TUPLE 0}    This would be the error message but there's no failure yet
    Should Be Empty    Now this will fail    My non-default error message

Should Not Be Empty
    [Documentation]    FAIL '{}' should not be empty.
    Should Not Be Empty    ${TUPLE 1}
    Should Not Be Empty    ${LIST 2
    Should Not Be Empty    ${DICT 3}
    Should Not Be Empty    ${CUSTOM 2}
    Should Not Be Empty    Non empty string
    Should Not Be Empty    ${DICT 0}

Should Not Be Empty With Non Default Message
    [Documentation]    FAIL My fine error says () is empty
    Should Not Be Empty    I'm not empty    This would be the error message but there's no failure yet
    Should Not Be Empty    ${TUPLE 0}    My fine error says ${TUPLE 0} is empty

Length With Length Method
    [Documentation]    FAIL 'length()' should be empty.
    Verify Get Length    ${LENGTH_METHOD}    40
    Length Should Be    ${LENGTH_METHOD}    40
    Should Not Be Empty    ${LENGTH_METHOD}
    Should Be Empty    ${LENGTH_METHOD}

Length With Size Method
    [Documentation]    FAIL 'size()' should be empty.
    Verify Get Length    ${SIZE_METHOD}    41
    Length Should Be    ${SIZE_METHOD}    41
    Should Not Be Empty    ${SIZE_METHOD}
    Should Be Empty    ${SIZE_METHOD}

Length With Length Attribute
    [Documentation]    FAIL 'length' should be empty.
    Verify Get Length    ${LENGTH_ATTRIBUTE}    42
    Length Should Be    ${LENGTH_ATTRIBUTE}    ${42}
    Should Not Be Empty    ${LENGTH_ATTRIBUTE}
    Should Be Empty    ${LENGTH_ATTRIBUTE}

Length Of Java Types
    # HashTable str changed from {foo=bar} to {foo: bar} in Jython 2.7b4
    [Documentation]    FAIL REGEXP: Length of '{a(=|: )1}' should be 3 but is 1.
    : FOR    ${type}    IN    STRING    HASHTABLE    VECTOR    ARRAY
    \    Verify Length Of Java Type    ${type}
    Length Should Be    ${HASHTABLE 1}    3

Should Contain X Times With String
    Should Contain X Times    hello    l    2
    Should Contain X Times    hello    ello    1
    Should Contain X Times    hello    hello    1
    Should Contain X Times    hello    x    0

Should Contain X Times With List
    Should Contain X Times    ${LIST}    cee    1
    Should Contain X Times    ${LIST}    b    2
    Should Contain X Times    ${LIST}    ${42}    1
    Should Contain X Times    ${LIST}    42    0

Should Contain X Times With Tuple
    Should Contain X Times    ${TUPLE3}    a    1

Should Contain X With Java Array And Vector
    Should Contain X Times    ${ARRAY3}    a    1
    Should Contain X Times    ${VECTOR3}    a    1

Should Contain X With Invalid Item
    [Documentation]    FAIL STARTS: Converting '10' to list failed: TypeError:
    Should Contain X Times    ${10}    a    1

Should Contain X Times With Invalid Count
    [Documentation]    FAIL STARTS: 'invalid' cannot be converted to an integer: ValueError:
    Should Contain X Times    hello    l    invalid

Should Contain X Times Failing With Default Message 1
    [Documentation]    FAIL 'hello' contains 'l' 2 times, not 3 times.
    Should Contain X Times    hello    l    3

Should Contain X Times Failing With Default Message 2
    [Documentation]    FAIL 'hello' contains 'lo' 1 time, not 0 times.
    Should Contain X Times    hello    lo    0

Should Contain X Times Failing With Default Message 3
    [Documentation]    FAIL 'hello' contains 'l' 2 times, not 1 time.
    Should Contain X Times    hello    l    1

Should Contain X Times Failing With Defined Message
    [Documentation]    FAIL My message
    Should Contain X Times    hello    nonex    3    My message

Get Count
    [Documentation]    This keyword is already tested pretty well by Should Contain X Times keyword that uses this one as a helper. FAIL STARTS: Converting 'None' to list failed: TypeError:
    Verify Get Count    Hello, world!    o    2
    Verify Get Count    ${LIST}    cee    1
    Verify Get Count    ${TUPLE3}    a    1
    Verify Get Count    ${SPACE * 100}    ${SPACE * 2}    50
    Verify Get Count    Hello, world!    no match here    0
    Get Count    ${None}    x

*** Keywords ***
Verify Get Length
    [Arguments]    ${item}    ${exp}
    ${length} =    Get Length    ${item}
    ${exp} =    Convert To Integer    ${exp}
    Should Be Equal    ${length}    ${exp}

Verify Get Count
    [Arguments]    ${item1}    ${item2}    ${exp}
    ${count} =    Get Count    ${item1}    ${item2}
    ${exp} =    Convert To Integer    ${exp}
    Should Be Equal    ${count}    ${exp}

Verify Length Of Java Type
    [Arguments]    ${type}
    : FOR    ${i}    IN RANGE    4
    \    Verify Get Length    ${${type} ${i}}    ${i}
    \    Length Should Be    ${${type} ${i}}    ${i}
    Should Not Be Empty    ${${type} 1}
    Should Be Empty    ${${type} 0}
