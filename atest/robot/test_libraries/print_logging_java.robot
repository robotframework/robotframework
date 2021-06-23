*** Settings ***
Documentation     Tests for logging using stdout/stderr
Suite Setup       Run Tests    --loglevel DEBUG    test_libraries/print_logging_java.robot
Force Tags        require-jython
Resource          atest_resource.robot

*** Test Cases ***
Logging Using Stdout And Stderr
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.setup.msgs[0]}    Hello\nworld\n!!
    Check Log Message    ${tc.kws[0].msgs[0]}    Hello from Java library!
    Check Log Message    ${tc.kws[1].msgs[0]}    Hello Java stderr!!
    Stderr Should Contain    Hello Java stderr!!

Logging Non-ASCII
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hyvää päivää java stdout!
    Check Log Message    ${tc.kws[1].msgs[0]}    Hyvää päivää java stderr!
    Stderr Should Contain    Hyvää päivää java stderr!

Logging with Levels
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    This is debug    DEBUG
    Check Log Message    ${tc.kws[1].msgs[0]}    First msg\n2nd line of1st msg    INFO
    Check Log Message    ${tc.kws[1].msgs[1]}    2nd msg *INFO* Still 2nd    INFO
    Check Log Message    ${tc.kws[2].msgs[0]}    1st msg\n2nd line
    Check Log Message    ${tc.kws[2].msgs[1]}    Second msg\n*INVAL* Still 2nd    WARN
    Check Log Message    ${tc.kws[2].msgs[2]}    Now 3rd msg
    Check Log Message    ${tc.kws[3].msgs[0]}    Warning to stderr    WARN
    Check Log Message    ${ERRORS.msgs[0]}    Second msg\n*INVAL* Still 2nd    WARN
    Check Log Message    ${ERRORS.msgs[1]}    Warning to stderr    WARN
    Stderr Should Contain    [ WARN ] Second msg\n*INVAL* Still 2nd\n
    Stderr Should Contain    [ WARN ] Warning to stderr\n*WARN* Warning to stderr

Logging HTML
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    <b>Hello, stdout!</b>    HTML
    Check Log Message    ${tc.kws[1].msgs[0]}    <b>Hello, stderr!</b>    HTML
    Stderr Should Contain    *HTML* <b>Hello, stderr!</b>

Logging both to Python and Java streams
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    First message to Python
    Check Log Message    ${tc.kws[0].msgs[1]}    Last message to Python
    Check Log Message    ${tc.kws[0].msgs[2]}    Second message to Java
