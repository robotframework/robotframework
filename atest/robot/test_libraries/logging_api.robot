*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/logging_api.robot
Resource        atest_resource.robot

*** Test Cases ***
Log levels
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 1]}     trace msg 1   TRACE
    Check Log Message    ${tc[1, 2]}     trace msg 2   TRACE
    Check Log Message    ${tc[1, 3]}     debug msg 1   DEBUG
    Check Log Message    ${tc[1, 4]}     debug msg 2   DEBUG
    Check Log Message    ${tc[1, 5]}     info msg 1    INFO
    Check Log Message    ${tc[1, 6]}     info msg 2    INFO
    Check Log Message    ${tc[1, 7]}     warn msg 1    WARN
    Check Log Message    ${tc[1, 8]}     warn msg 2    WARN
    Check Log Message    ${tc[1, 9]}     error msg 1   ERROR
    Check Log Message    ${tc[1, 10]}    error msg 2   ERROR
    Check Log Message    ${ERRORS[0]}    warn msg 1    WARN
    Check Log Message    ${ERRORS[1]}    warn msg 2    WARN
    Check Log Message    ${ERRORS[2]}    error msg 1   ERROR
    Check Log Message    ${ERRORS[3]}    error msg 2   ERROR

Invalid level
    Check Test Case    ${TEST NAME}

FAIL is not valid log level
    Check Test Case    ${TEST NAME}

Timestamps are accurate
    ${tc} =    Check Test Case    ${TEST NAME}
    ${msg1}    ${msg2} =    Set variable    ${tc[0].messages}
    Check Log Message    ${msg1}    First message
    Check Log Message    ${msg2}    Second message 0.1 sec later
    Should be true    '${msg1.timestamp}' < '${msg2.timestamp}'

Log HTML
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 0]}      <b>debug</b>    DEBUG    html=True
    Check Log Message    ${tc[1, 1]}      <b>info</b>     INFO     html=True
    Check Log Message    ${tc[1, 2]}      <b>warn</b>     WARN     html=True
    Check Log Message    ${ERRORS[4]}     <b>warn</b>     WARN     html=True

Write messages to console
    ${tc} =    Check Test Case    ${TEST NAME}
    Stdout Should Contain    To console only
    Stdout Should Contain    To console in two parts
    Stdout Should Contain    To log and console
    Check Log Message    ${tc[0, 0]}    To log and console    INFO

Log non-strings
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}     42
    Check Log Message    ${tc[0, 1]}     True    WARN    html=True
    Check Log Message    ${tc[0, 2]}     None
    Check Log Message    ${ERRORS[5]}    True    WARN    html=True

Log callable
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}    <function log_callable at *>    pattern=True
