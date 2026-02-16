*** Settings ***
Suite Setup       Run Tests
...               --listener ${CURDIR}/listener_using_builtin.py
...               standard_libraries/builtin/used_in_custom_libs_and_listeners.robot
Resource          atest_resource.robot

*** Test Cases ***
Keywords Using BuiltIn
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Log level changed from NONE to DEBUG.    DEBUG
    Check Log Message    ${tc[0, 1]}    Hello, debug world!    DEBUG
    Length should be     ${tc[0].messages}    2

Named argument syntax
    Check Test Case    ${TESTNAME}

Listener Using BuiltIn
    Check Test Case    ${TESTNAME}

Use 'Run Keyword' with non-Unicode values
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0]}    42
    Check Log Message    ${tc[0, 1, 0]}    \xff

Use BuiltIn keywords with timeouts
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}       Log level changed from NONE to DEBUG.    DEBUG
    Check Log Message    ${tc[0, 1]}       Hello, debug world!    DEBUG
    Length should be     ${tc[0].messages}    2
    Check Log Message    ${tc[3, 0]}       Test timeout 1 day active. * seconds left.    level=DEBUG    pattern=True
    Check Log Message    ${tc[3, 1, 0]}    Test timeout 1 day active. * seconds left.    level=DEBUG    pattern=True
    Check Log Message    ${tc[3, 1, 1]}    42
    Check Log Message    ${tc[3, 2, 0]}    Test timeout 1 day active. * seconds left.    level=DEBUG    pattern=True
    Check Log Message    ${tc[3, 2, 1]}    \xff

User keyword used via 'Run Keyword'
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}          Before
    Check Log Message    ${tc[0, 1, 0, 0]}    This is x-911-zzz
    Check Log Message    ${tc[0, 2]}          After

User keyword used via 'Run Keyword' with timeout and trace level
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}          Arguments: [ \ ]    level=TRACE
    Check Log Message    ${tc[0, 1]}          Test timeout 1 day active. * seconds left.    level=DEBUG    pattern=True
    Check Log Message    ${tc[0, 2]}          Before
    Check Log Message    ${tc[0, 3, 0]}       Arguments: [ \${x}='This is x' | \${y}=911 | \${z}='zzz' ]    level=TRACE
    Check Log Message    ${tc[0, 3, 1, 0]}    Arguments: [ 'This is x-911-zzz' ]    level=TRACE
    Check Log Message    ${tc[0, 3, 1, 1]}    Keyword timeout 1 hour active. * seconds left.    level=DEBUG    pattern=True
    Check Log Message    ${tc[0, 3, 1, 2]}    This is x-911-zzz
    Check Log Message    ${tc[0, 3, 1, 3]}    Return: None    level=TRACE
    Check Log Message    ${tc[0, 3, 2]}       Return: None    level=TRACE
    Check Log Message    ${tc[0, 4]}          After
    Check Log Message    ${tc[0, 5]}          Return: None    level=TRACE

Recursive 'Run Keyword' usage
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 0]}    1
    Check Log Message    ${tc[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]}    10

Recursive 'Run Keyword' usage with timeout
    Check Test Case    ${TESTNAME}

Timeout when running keyword that logs huge message
    Check Test Case    ${TESTNAME}

Timeout in parent keyword after running keyword
    Check Test Case    ${TESTNAME}
