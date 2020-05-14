*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/logging_api.robot
Resource        atest_resource.robot

*** Test Cases ***
Log levels
    ${tc} =  Check test case  ${TEST NAME}
    Check log message  ${tc.kws[1].msgs[1]}  trace msg 1  TRACE
    Check log message  ${tc.kws[1].msgs[2]}  trace msg 2  TRACE
    Check log message  ${tc.kws[1].msgs[3]}  debug msg 1  DEBUG
    Check log message  ${tc.kws[1].msgs[4]}  debug msg 2  DEBUG
    Check log message  ${tc.kws[1].msgs[5]}  info msg 1   INFO
    Check log message  ${tc.kws[1].msgs[6]}  info msg 2   INFO
    Check log message  ${tc.kws[1].msgs[7]}  warn msg 1   WARN
    Check log message  ${tc.kws[1].msgs[8]}  warn msg 2   WARN
    Check log message  ${tc.kws[1].msgs[9]}  error msg 1   ERROR
    Check log message  ${tc.kws[1].msgs[10]}  error msg 2   ERROR
    Check log message  ${ERRORS[0]}    warn msg 1   WARN
    Check log message  ${ERRORS[1]}    warn msg 2   WARN
    Check log message  ${ERRORS[2]}    error msg 1   ERROR
    Check log message  ${ERRORS[3]}    error msg 2   ERROR

Invalid level
    Check test case  ${TEST NAME}

FAIL is not valid log level
    Check test case  ${TEST NAME}

Timestamps are accurate
    ${tc} =  Check test case  ${TEST NAME}
    ${msg1}    ${msg2} =  Set variable  ${tc.kws[0].msgs}
    Check log message  ${msg1}  First message
    Check log message  ${msg2}  Second message 0.1 sec later
    Should be true  '${msg1.timestamp}' < '${msg2.timestamp}'

Log HTML
    ${tc} =  Check test case  ${TEST NAME}
    Check log message  ${tc.kws[1].msgs[0]}  <b>debug</b>  DEBUG  html=True
    Check log message  ${tc.kws[1].msgs[1]}  <b>info</b>   INFO   html=True
    Check log message  ${tc.kws[1].msgs[2]}  <b>warn</b>   WARN   html=True
    Check log message  ${ERRORS.msgs[4]}     <b>warn</b>   WARN   html=True

Write messages to console
    ${tc} =  Check test case  ${TEST NAME}
    Stdout Should Contain  To console only
    Stdout Should Contain  To console in two parts
    Stdout Should Contain  To log and console
    Check log message  ${tc.kws[0].msgs[0]}  To log and console  INFO

Log Non-Strings
    ${tc} =  Check test case  ${TEST NAME}
    Check log message  ${tc.kws[0].msgs[0]}  42
    Check log message  ${tc.kws[0].msgs[1]}  True  WARN
    Check log message  ${ERRORS.msgs[5]}  True  WARN

Log Callable
    ${tc} =  Check test case  ${TEST NAME}
    Check log message  ${tc.kws[0].msgs[0]}  <function log_callable at *>  pattern=yes
