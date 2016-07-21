*** Settings ***
Documentation   Tests for libs logging during import and in init/constructor.
Suite Setup     Run Tests  --PYTHONPATH "${DATADIR}/test_libraries"  test_libraries/import_and_init_logging.robot
Resource        atest_resource.robot

*** Test Cases ***

Test case should not get import/init messages
    ${tc} =  Check test case  No import/init time messages here
    Should be empty  ${tc.kws[0].msgs}
    Should be empty  ${tc.kws[1].msgs}

Python library logging at import via stdout and stderr
    Check syslog contains  | WARN \ | Warning via stdout in import\n
    Check syslog contains  | INFO \ | Info via stderr in import\n
    Check stderr contains  [ WARN ] Warning via stdout in import\n
    Check stderr contains  \nInfo via stderr in import\n

Python library logging at import via logging API
    Check syslog contains  | WARN \ | Warning via API in import\n
    Check stderr contains  [ WARN ] Warning via API in import\n

Python library logging in import via stdout and stderr
    Check syslog contains  | WARN \ | Warning via stdout in init 1\n
    Check syslog contains  | WARN \ | Warning via stdout in init 2\n
    Check syslog contains  | INFO \ | Info via stderr in init 1\n
    Check syslog contains  | INFO \ | Info via stderr in init 2\n
    Check stderr contains  [ WARN ] Warning via stdout in init 1\n
    Check stderr contains  [ WARN ] Warning via stdout in init 2\n
    Check stderr contains  \nInfo via stderr in init 1\n
    Check stderr contains  \nInfo via stderr in init 2\n

Python library logging in import via logging API
    Check syslog contains  | WARN \ | Warning via API in init 1\n
    Check syslog contains  | WARN \ | Warning via API in init 2\n
    Check stderr contains  [ WARN ] Warning via API in init 1\n
    Check stderr contains  [ WARN ] Warning via API in init 2\n

Java library logging in constructor via stdout and stderr
    [Tags]  require-jython
    ${tc} =  Check test case  No import/init time messages in Java either
    Should be empty  ${tc.kws[0].msgs}
    Check syslog contains  | WARN \ | Warning via stdout in constructor 1\n
    Check syslog contains  | WARN \ | Warning via stdout in constructor 2\n
    Check syslog contains  | INFO \ | Info via stderr in constructor 1\n
    Check syslog contains  | INFO \ | Info via stderr in constructor 2\n
    Check stderr contains  [ WARN ] Warning via stdout in constructor 1\n
    Check stderr contains  [ WARN ] Warning via stdout in constructor 2\n
    Check stderr contains  \nInfo via stderr in constructor 1
    Check stderr contains  \nInfo via stderr in constructor 2

Importing and initializing libraries in init
    ${tc} =  Check Test Case  ${TEST NAME}
    Check log message  ${tc.kws[0].msgs[0]}  Keyword from library with importing __init__.
    Check log message  ${tc.kws[2].msgs[0]}  Keyword from library with initting __init__.
    Check log message  ${tc.kws[2].msgs[1]}  Keyword from library initted by __init__ (id: 42).
    Check log message  ${tc.kws[3].msgs[0]}  Keyword from library initted by __init__ (id: 42).
