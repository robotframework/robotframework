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
    Stdout Should Contain    Hello, console!\n
    Stdout Should Contain    ${HTML}\n

repr=True
    [Documentation]    In RF 3.1.2 `formatter=repr` and `repr=True` yield same
    ...                results and thus these tests are identical.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    'Nothing special here'
    Check Log Message    ${tc.kws[1].msgs[0]}    'Hyvää yötä ☃!'
    Check Log Message    ${tc.kws[2].msgs[0]}    42    DEBUG
    Check Log Message    ${tc.kws[4].msgs[0]}    b'\\x00abc\\xff (repr=True)'
    Check Log Message    ${tc.kws[6].msgs[0]}    'hyvä'
    Stdout Should Contain    b'\\x00abc\\xff (repr=True)'

formatter=repr
    [Documentation]    In RF 3.1.2 `formatter=repr` and `repr=True` yield same
    ...                results and thus these tests are identical.
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    'Nothing special here'
    Check Log Message    ${tc.kws[1].msgs[0]}    'Hyvää yötä ☃!'
    Check Log Message    ${tc.kws[2].msgs[0]}    42    DEBUG
    Check Log Message    ${tc.kws[4].msgs[0]}    b'\\x00abc\\xff (formatter=repr)'
    Check Log Message    ${tc.kws[6].msgs[0]}    'hyvä'
    Stdout Should Contain    b'\\x00abc\\xff (formatter=repr)'

formatter=ascii
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    'Nothing special here'
    Check Log Message    ${tc.kws[1].msgs[0]}    'Hyv\\xe4\\xe4 y\\xf6t\\xe4 \\u2603!'
    Check Log Message    ${tc.kws[2].msgs[0]}    42    DEBUG
    Check Log Message    ${tc.kws[4].msgs[0]}    b'\\x00abc\\xff (formatter=ascii)'
    Check Log Message    ${tc.kws[6].msgs[0]}    'hyva\\u0308'
    Stdout Should Contain    b'\\x00abc\\xff (formatter=ascii)'

formatter=str
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Nothing special here
    Check Log Message    ${tc.kws[1].msgs[0]}    Hyvää yötä ☃!
    Check Log Message    ${tc.kws[2].msgs[0]}    42    DEBUG
    Check Log Message    ${tc.kws[4].msgs[0]}    abc\\xff (formatter=str)
    Check Log Message    ${tc.kws[6].msgs[0]}    hyvä
    Stdout Should Contain    abc\\xff (formatter=str)

formatter=repr pretty prints
    ${tc} =    Check Test Case    ${TEST NAME}
    ${long string} =    Evaluate    ' '.join(['Robot Framework'] * 1000)
    ${small dict} =    Set Variable    {3: b'items', 'a': 'sorted', 'small': 'dict'}
    ${small list} =    Set Variable    ['small', b'list', 'not sorted', 4]
    Check Log Message    ${tc.kws[1].msgs[0]}    '${long string}'
    Check Log Message    ${tc.kws[3].msgs[0]}    ${small dict}
    Check Log Message    ${tc.kws[5].msgs[0]}    {'big': 'dict',\n\ 'list': [1, 2, 3],\n\ 'long': '${long string}',\n\ 'nested': ${small dict}}
    Check Log Message    ${tc.kws[7].msgs[0]}    ${small list}
    Check Log Message    ${tc.kws[9].msgs[0]}    ['big',\n\ 'list',\n\ '${long string}',\n\ b'${long string}',\n\ ['nested', ('tuple', 2)],\n\ ${small dict}]
    Check Log Message    ${tc.kws[11].msgs[0]}    ['hyvä', b'hyv\\xe4', {'☃': b'\\x00\\xff'}]
    Stdout Should Contain    ${small dict}
    Stdout Should Contain    ${small list}

formatter=invalid
    Check Test Case    ${TEST NAME}

Log callable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    *objects_for_call_method.MyObject*    pattern=yes
    Check Log Message    ${tc.kws[2].msgs[0]}    <function <lambda*> at *>    pattern=yes

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
    FOR    ${i}    IN RANGE    4
        Should Be Empty    ${tc.kws[${i}].msgs}
    END
    Stdout Should Contain    stdout äö w/ newline\n
    Stdout Should Contain    stdout äö w/o new......line äö
    Stderr Should Contain    stderr äö w/ newline\n
    Stdout Should Contain    42
