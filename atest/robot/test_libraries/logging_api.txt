*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/logging_api.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

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
    Check log message  ${ERRORS.msgs[0]}     warn msg 1   WARN
    Check log message  ${ERRORS.msgs[1]}     warn msg 2   WARN

Timestamps are accurate
    ${tc} =  Check test case  ${TEST NAME}
    ${msgs} =  Set variable  ${tc.kws[0].msgs}
    Check log message  ${msgs[0]}  First message
    Check log message  ${msgs[1]}  Second message 0.1 sec later
    Should be true  '${msgs[0].timestamp}' < '${msgs[1].timestamp}'

Log HTML
    ${tc} =  Check test case  ${TEST NAME}
    Check log message  ${tc.kws[1].msgs[0]}  <b>debug</b>  DEBUG  html=True
    Check log message  ${tc.kws[1].msgs[1]}  <b>info</b>   INFO   html=True
    Check log message  ${tc.kws[1].msgs[2]}  <b>warn</b>   WARN   html=True
    Check log message  ${ERRORS.msgs[2]}     <b>warn</b>   WARN   html=True

Write messages to console
    ${tc} =  Check test case  ${TEST NAME}
    Check stdout contains  To console only
    Check stdout contains  To console in two parts
    Check stdout contains  To log and console
    Check log message  ${tc.kws[0].msgs[0]}  To log and console  INFO

Log Non-Strings
    ${tc} =  Check test case  ${TEST NAME}
    Check log message  ${tc.kws[0].msgs[0]}  42
    Check log message  ${tc.kws[0].msgs[1]}  True  WARN
    Check log message  ${ERRORS.msgs[3]}  True  WARN

Log Callable
    ${tc} =  Check test case  ${TEST NAME}
    Check log message  ${tc.kws[0].msgs[0]}  <function log_callable at *>  pattern=yes
