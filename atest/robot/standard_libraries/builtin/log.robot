*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/log.robot
Resource          atest_resource.robot

*** Variables ***
${HTML}           <a href="http://robotframework.org">Robot Framework</a>

*** Test Cases ***
Log
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hello, world!
    Check Log Message    ${tc.kws[1].msgs[0]}    42
    Check Log Message    ${tc.kws[2].msgs[0]}    None
    Check Log Message    ${tc.kws[3].msgs[0]}    String presentation of MyObject

Log with different levels
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Log says: Hello from tests!    INFO
    Check Log Message    ${tc.kws[1].msgs[1]}    Trace level    TRACE
    Check Log Message    ${tc.kws[2].msgs[1]}    Debug level    DEBUG
    Check Log Message    ${tc.kws[3].msgs[1]}    Info level     INFO
    Check Log Message    ${tc.kws[4].msgs[1]}    Warn level     WARN
    Check Log Message    ${tc.kws[5].msgs[1]}    Error level    ERROR
    Check Log Message    ${ERRORS[0]}            Warn level     WARN
    Check Log Message    ${ERRORS[1]}            Error level    ERROR
    Length Should Be     ${ERRORS}               2

HTML is escaped by default
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    <b>not bold</b>
    Check Log Message    ${tc.kws[1].msgs[0]}    ${HTML}

HTML pseudo level
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    <b>bold</b>    html=True
    Check Log Message    ${tc.kws[1].msgs[0]}    ${HTML}    html=True

Explicit HTML
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    <b>bold</b>    html=True
    Check Log Message    ${tc.kws[1].msgs[0]}    ${HTML}    DEBUG    html=True
    Check Log Message    ${tc.kws[2].msgs[0]}    ${HTML}    DEBUG

FAIL is not valid log level
    Check Test Case    ${TEST NAME}

Log also to console
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hello, console!
    Check Log Message    ${tc.kws[1].msgs[0]}    ${HTML}    DEBUG    html=True
    Check Stdout Contains    Hello, console!\n
    Check Stdout Contains    ${HTML}\n

Log repr
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    'Nothing special here'
    ${expected} =    Set Variable If    ${INTERPRETER.is_py2}    'Hyv\\xe4\\xe4 y\\xf6t\\xe4 \\u2603!'    'Hyv\xe4\xe4 y\xf6t\xe4 \u2603!'
    Check Log Message    ${tc.kws[1].msgs[0]}    ${expected}
    Check Log Message    ${tc.kws[2].msgs[0]}    42    DEBUG
    Check Log Message    ${tc.kws[4].msgs[0]}    b'\\x00\\xff'
    ${expected} =    Set Variable If    ${INTERPRETER.is_py2}    ['Hyv\\xe4', '\\u2603', 42, b'\\x00\\xff']    ['Hyv\xe4', '\u2603', 42, b'\\x00\\xff']
    Check Log Message    ${tc.kws[6].msgs[0]}    ${expected}
    Check Stdout Contains    ${expected}

Log pprint
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}'a longer string!',\n${SPACE * 10}'a much, much, much, much, much, much longer string']}
    Check Stdout Contains    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}'a longer string!',\n${SPACE * 10}'a much, much, much, much, much, much longer string']}
    Check Log Message    ${tc.kws[3].msgs[0]}    [b'One', 'Two', 3]
    Check Stdout Contains    [b'One', 'Two', 3]
    Check Log Message    ${tc.kws[5].msgs[0]}    [b'a long string',\n${SPACE}'a longer string!',\n${SPACE}'a much, much, much, much, much, much longer string']
    Check Stdout Contains    [b'a long string',\n${SPACE}'a longer string!',\n${SPACE}'a much, much, much, much, much, much longer string']
    Check Log Message    ${tc.kws[7].msgs[0]}    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}'a longer string!',\n${SPACE * 10}'a much, much, much, much, much, much longer string']}
    Check Log Message    ${tc.kws[9].msgs[0]}    ['One', b'Two', 3]
    ${expected} =    Set Variable If    ${INTERPRETER.is_py2}
    ...    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}42,\n${SPACE * 10}'Hyv\\xe4\\xe4 y\\xf6t\\xe4 \\u2603!',\n${SPACE * 10}'a much, much, much, much, much, much longer string',\n${SPACE * 10}b'\\x00\\xff']}
    ...    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}42,\n${SPACE * 10}'Hyv\xe4\xe4 y\xf6t\xe4 \u2603!',\n${SPACE * 10}'a much, much, much, much, much, much longer string',\n${SPACE * 10}b'\\x00\\xff']}
    Check Log Message    ${tc.kws[11].msgs[0]}    ${expected}
    Check Stdout Contains    ${expected}

Log callable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    *objects_for_call_method.MyObject*    pattern=yes
    Check Log Message    ${tc.kws[2].msgs[0]}    <function <lambda> at *>    pattern=yes

Log Many
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Log Many says:
    Check Log Message    ${tc.kws[0].msgs[1]}    1
    Check Log Message    ${tc.kws[0].msgs[2]}    2
    Check Log Message    ${tc.kws[0].msgs[3]}    3
    Check Log Message    ${tc.kws[0].msgs[4]}    String presentation of MyObject
    Check Log Message    ${tc.kws[1].msgs[0]}    Log Many says: Hi!!
    Check Log Message    ${tc.kws[2].msgs[0]}    1
    Check Log Message    ${tc.kws[2].msgs[1]}    2
    Check Log Message    ${tc.kws[2].msgs[2]}    3
    Check Log Message    ${tc.kws[2].msgs[3]}    String presentation of MyObject
    Should Be Empty    ${tc.kws[3].msgs}
    Should Be Empty    ${tc.kws[4].msgs}
    Check Log Message    ${tc.kws[5].msgs[0]}    --
    Check Log Message    ${tc.kws[5].msgs[1]}    -[]-
    Check Log Message    ${tc.kws[5].msgs[2]}    -{}-
    Check Log Message    ${tc.kws[6].msgs[0]}    1
    Check Log Message    ${tc.kws[6].msgs[1]}    2

Log Many with named and dict arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    a=1
    Check Log Message    ${tc.kws[0].msgs[1]}    b=2
    Check Log Message    ${tc.kws[0].msgs[2]}    3=c
    Check Log Message    ${tc.kws[0].msgs[3]}    obj=String presentation of MyObject
    Check Log Message    ${tc.kws[1].msgs[0]}    a=1
    Check Log Message    ${tc.kws[1].msgs[1]}    b=2
    Check Log Message    ${tc.kws[1].msgs[2]}    3=c
    Check Log Message    ${tc.kws[1].msgs[3]}    obj=String presentation of MyObject
    Check Log Message    ${tc.kws[2].msgs[0]}    a=1
    Check Log Message    ${tc.kws[2].msgs[1]}    b=2
    Check Log Message    ${tc.kws[2].msgs[2]}    3=c
    Check Log Message    ${tc.kws[2].msgs[3]}    obj=String presentation of MyObject
    Check Log Message    ${tc.kws[2].msgs[4]}    b=no override
    Check Log Message    ${tc.kws[2].msgs[5]}    3=three

Log Many with positional, named and dict arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    1
    Check Log Message    ${tc.kws[0].msgs[1]}    2
    Check Log Message    ${tc.kws[0].msgs[2]}    three=3
    Check Log Message    ${tc.kws[0].msgs[3]}    4=four
    Check Log Message    ${tc.kws[1].msgs[0]}    1
    Check Log Message    ${tc.kws[1].msgs[1]}    2
    Check Log Message    ${tc.kws[1].msgs[2]}    3
    Check Log Message    ${tc.kws[1].msgs[3]}    String presentation of MyObject
    Check Log Message    ${tc.kws[1].msgs[4]}    a=1
    Check Log Message    ${tc.kws[1].msgs[5]}    b=2
    Check Log Message    ${tc.kws[1].msgs[6]}    3=c
    Check Log Message    ${tc.kws[1].msgs[7]}    obj=String presentation of MyObject
    Check Log Message    ${tc.kws[1].msgs[8]}    1
    Check Log Message    ${tc.kws[1].msgs[9]}    2
    Check Log Message    ${tc.kws[1].msgs[10]}    3
    Check Log Message    ${tc.kws[1].msgs[11]}    String presentation of MyObject
    Check Log Message    ${tc.kws[1].msgs[12]}    a=1
    Check Log Message    ${tc.kws[1].msgs[13]}    b=2
    Check Log Message    ${tc.kws[1].msgs[14]}    3=c
    Check Log Message    ${tc.kws[1].msgs[15]}    obj=String presentation of MyObject

Log Many with non-existing variable
    Check Test Case    ${TEST NAME}

Log Many with list variable containing non-list
    Check Test Case    ${TEST NAME}

Log Many with dict variable containing non-dict
    Check Test Case    ${TEST NAME}

Log To Console
    ${tc} =    Check Test Case    ${TEST NAME}
    :FOR    ${i}    IN RANGE    4
    \    Should Be Empty    ${tc.kws[${i}].msgs}
    Check Stdout Contains    stdout äö w/ newline\n
    Check Stdout Contains    stdout äö w/o new......line äö
    Check Stderr Contains    stderr äö w/ newline\n
    Check Stdout Contains    42
