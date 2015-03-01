*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/log.robot
Force Tags        regression    jybot    pybot
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
    Comment    Test set log level to trace so    the logged message is second    and first contains resolved args
    Check Log Message    ${tc.kws[0].msgs[1]}    Log says: Hello from tests!    INFO
    Check Log Message    ${tc.kws[1].msgs[1]}    Trace level    TRACE
    Check Log Message    ${tc.kws[2].msgs[1]}    Debug level    DEBUG
    Check Log Message    ${tc.kws[3].msgs[1]}    Info level    INFO
    Check Log Message    ${tc.kws[4].msgs[1]}    Warn level    WARN
    Length Should Be    ${tc.kws[4].msgs}    3
    Check Log Message    ${ERRORS.msgs[0]}    Warn level    WARN
    Check Log Message    ${tc.kws[5].msgs[1]}    Fail level    FAIL
    Check Log Message    ${tc.kws[6].msgs[1]}    Error level    ERROR

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

Log also to console
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hello, console!
    Check Log Message    ${tc.kws[1].msgs[0]}    ${HTML}    DEBUG    html=True
    Check Stdout Contains    Hello, console!\n
    Check Stdout Contains    ${HTML}\n

Log repr
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    'Hyv\\xe4\\xe4 y\\xf6t\\xe4 \\u2603!'
    Check Log Message    ${tc.kws[1].msgs[0]}    42    DEBUG
    ${bytes} =    Set Variable If    not "${IRONPYTHON}"    b'\\x00\\xff'    '\\x00\\xff'
    Check Log Message    ${tc.kws[3].msgs[0]}    ${bytes}
    Check Log Message    ${tc.kws[5].msgs[0]}    ['Hyv\\xe4', '\\u2603', 42, ${bytes}]
    Check Stdout Contains    ['Hyv\\xe4', '\\u2603', 42, ${bytes}]

Log pprint
    ${tc} =    Check Test Case    ${TEST NAME}
    ${b} =    Set Variable If    not "${IRONPYTHON}"    b    ${EMPTY}
    Check Log Message    ${tc.kws[1].msgs[0]}    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}'a longer string!',\n${SPACE * 10}'a much, much, much, much, much, much longer string']}
    Check Stdout Contains    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}'a longer string!',\n${SPACE * 10}'a much, much, much, much, much, much longer string']}
    Check Log Message    ${tc.kws[3].msgs[0]}    [${b}'One', 'Two', 3]
    Check Stdout Contains    [${b}'One', 'Two', 3]
    Check Log Message    ${tc.kws[5].msgs[0]}    [${b}'a long string',\n${SPACE}'a longer string!',\n${SPACE}'a much, much, much, much, much, much longer string']
    Check Stdout Contains    [${b}'a long string',\n${SPACE}'a longer string!',\n${SPACE}'a much, much, much, much, much, much longer string']
    Check Log Message    ${tc.kws[7].msgs[0]}    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}'a longer string!',\n${SPACE * 10}'a much, much, much, much, much, much longer string']}
    Check Log Message    ${tc.kws[9].msgs[0]}    ['One', ${b}'Two', 3]
    Check Log Message    ${tc.kws[11].msgs[0]}    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}42,\n${SPACE * 10}'Hyv\\xe4\\xe4 y\\xf6t\\xe4 \\u2603!',\n${SPACE * 10}'a much, much, much, much, much, much longer string',\n${SPACE * 10}${b}'\\x00\\xff']}
    Check Stdout Contains    {'a long string': 1,\n${SPACE}'a longer string!': 2,\n${SPACE}'a much, much, much, much, much, much longer string': 3,\n${SPACE}'list': ['a long string',\n${SPACE * 10}42,\n${SPACE * 10}'Hyv\\xe4\\xe4 y\\xf6t\\xe4 \\u2603!',\n${SPACE * 10}'a much, much, much, much, much, much longer string',\n${SPACE * 10}${b}'\\x00\\xff']}

Log callable
    ${tc} =    Check Test Case    ${TEST NAME}
    Run on python 3.x
    ...    Check Log Message    ${tc.kws[0].msgs[0]}    <class 'objects_for_call_method.MyObject'>
    Run on python 2.x
    ...    Check Log Message    ${tc.kws[0].msgs[0]}    objects_for_call_method.MyObject

Log Many
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Log Many says:    INFO
    Check Log Message    ${tc.kws[0].msgs[1]}    Hello    INFO
    Check Log Message    ${tc.kws[0].msgs[2]}    from    INFO
    Check Log Message    ${tc.kws[0].msgs[3]}    tests!    INFO
    Check Log Message    ${tc.kws[1].msgs[0]}    Log Many says: Hi!!    INFO

Log To Console
    ${tc} =    Check Test Case    ${TEST NAME}
    :FOR    ${i}    IN RANGE    4
    \    Should Be Empty    ${tc.kws[${i}].msgs}
    Check Stdout Contains    stdout äö w/ newline\n
    Check Stdout Contains    stdout äö w/o new......line äö
    Check Stderr Contains    stderr äö w/ newline\n
    Check Stdout Contains    42

