*** Settings ***
Documentation     Tests for logging using stdout/stderr
Suite Setup       Run Tests    --loglevel DEBUG    test_libraries/print_logging.robot
Force Tags        regression    pybot    jybot
Resource          atest_resource.robot

*** Test Cases ***
Logging Using Stdout And Stderr
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hello from Python Library!
    Check Log Message    ${tc.kws[1].msgs[0]}    Hello to stderr from Python Library!
    Check Log Message    ${tc.kws[2].msgs[0]}    stdout: Hello!!
    Check Log Message    ${tc.kws[2].msgs[1]}    stderr: Hello!!
    Check Stderr Contains    Hello to stderr from Python Library!\nstderr: Hello!!

Logging Non-ASCII As Unicode
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Hyvää päivää stdout!
    Check Log Message    ${tc.kws[1].msgs[0]}    Hyvää päivää stderr!
    Check Stderr Contains    Hyvää päivää stderr!

Logging Non-ASCII As Bytes
    [Tags]    x-fails-on-ipy
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[2].msgs[0]}    Hyvää päivää!
    Check Log Message    ${tc.kws[3].msgs[0]}    Hyvää päivää!
    Check Stderr Contains    Hyvää päivää!

Logging Mixed Non-ASCII Unicode And Bytes
    [Tags]    x-fails-on-ipy
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[2].msgs[0]}    Hyvä byte! Hyvä Unicode!

Logging HTML
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    <a href="http://www.google.com">Google</a>    HTML
    Check Log Message    ${tc.kws[1].msgs[0]}    <table border=1>\n<tr><td>0,0</td><td>0,1</td></tr>\n <tr><td>1,0</td><td>1,1</td></tr>\n</table>    HTML
    Check Log Message    ${tc.kws[1].msgs[1]}    This is html <hr>    HTML
    Check Log Message    ${tc.kws[1].msgs[2]}    This is not html <br>    INFO
    Check Log Message    ${tc.kws[2].msgs[0]}    <i>Hello, stderr!!</i>    HTML
    Check Stderr Contains    *HTML* <i>Hello, stderr!!</i>
