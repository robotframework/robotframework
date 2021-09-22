*** Settings ***
Documentation     Tests for logging using stdout/stderr
Suite Setup       Run Tests
...    -v CONSOLE_ENCODING:${CONSOLE_ENCODING}
...    test_libraries/print_logging.robot
Resource          atest_resource.robot

*** Test Cases ***
Logging Using Stdout And Stderr
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hello from Python Library!
    Check Log Message    ${tc.kws[1].msgs[0]}    Hello to stderr from Python Library!
    Check Log Message    ${tc.kws[2].msgs[0]}    stdout: Hello!!
    Check Log Message    ${tc.kws[2].msgs[1]}    stderr: Hello!!
    Stderr Should Contain    Hello to stderr from Python Library!\nstderr: Hello!!

Logging with levels
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Trace message    TRACE
    Check Log Message    ${tc.kws[0].msgs[2]}    Debug message    DEBUG
    Check Log Message    ${tc.kws[0].msgs[3]}    Info message     INFO
    Check Log Message    ${tc.kws[0].msgs[4]}    Html message     INFO    html=True
    Check Log Message    ${tc.kws[0].msgs[5]}    Warn message     WARN
    Check Log Message    ${tc.kws[0].msgs[6]}    Error message    ERROR
    Check Log Message    ${ERRORS[0]}    Warn message     WARN
    Check Log Message    ${ERRORS[1]}    Error message    ERROR

Message before first level is considered INFO
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hello        INFO
    Check Log Message    ${tc.kws[0].msgs[1]}    world!       INFO
    Check Log Message    ${tc.kws[1].msgs[0]}    Hi\nthere    INFO
    Check Log Message    ${tc.kws[1].msgs[1]}    again!       DEBUG

Level must be all caps and start a row
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    *DeBUG* is not debug      INFO
    Check Log Message    ${tc.kws[1].msgs[0]}    This is not an *ERROR*    INFO

Logging Non-ASCII As Unicode
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hyvää päivää stdout!
    Check Log Message    ${tc.kws[1].msgs[0]}    Hyvää päivää stderr!
    Stderr Should Contain    Hyvää päivää stderr!

Logging Non-ASCII As Bytes
    ${tc} =    Check Test Case    ${TEST NAME}
    ${expected} =    Get Expected Bytes    Hyvää päivää!
    Check Log Message    ${tc.kws[1].msgs[0]}    ${expected}
    Check Log Message    ${tc.kws[2].msgs[0]}    ${expected}
    Stderr Should Contain    ${expected}

Logging Mixed Non-ASCII Unicode And Bytes
    ${tc} =    Check Test Case    ${TEST NAME}
    ${bytes} =    Get Expected Bytes    Hyvä byte!
    Check Log Message    ${tc.kws[1].msgs[0]}    ${bytes} Hyvä Unicode!

Logging HTML
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    <a href="http://www.google.com">Google</a>    HTML
    Check Log Message    ${tc.kws[1].msgs[0]}    <table border=1>\n<tr><td>0,0</td><td>0,1</td></tr>\n<tr><td>1,0</td><td>1,1</td></tr>\n</table>    HTML
    Check Log Message    ${tc.kws[1].msgs[1]}    This is html <hr>    HTML
    Check Log Message    ${tc.kws[1].msgs[2]}    This is not html <br>    INFO
    Check Log Message    ${tc.kws[2].msgs[0]}    <i>Hello, stderr!!</i>    HTML
    Stderr Should Contain    *HTML* <i>Hello, stderr!!</i>

FAIL is not valid log level
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    *FAIL* is not failure    INFO

*** Keywords ***
Get Expected Bytes
    [Arguments]    ${string}
    ${bytes} =    Encode String To Bytes    ${string}    ${CONSOLE_ENCODING}
    [Return]    b'${bytes}'
