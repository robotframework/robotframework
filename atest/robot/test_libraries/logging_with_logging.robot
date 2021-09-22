*** Settings ***
Documentation     Tests for logging using Python's `logging` module.
Suite Setup       Run Tests    -L none    test_libraries/logging_with_logging.robot
Resource          atest_resource.robot

*** Test Cases ***
All logging is disabled
    ${tc} =    Check test case    ${TEST NAME}
    Should be empty    ${tc.kws[0].msgs}
    Should be empty    ${tc.kws[1].msgs}

Log with default levels
    ${tc} =    Check test case    ${TEST NAME}
    Check log message    ${tc.kws[0].msgs[0]}    debug message    DEBUG
    Check log message    ${tc.kws[0].msgs[1]}    info message    INFO
    Check log message    ${tc.kws[0].msgs[2]}    warning message    WARN
    Check log message    ${tc.kws[0].msgs[3]}    error message    ERROR
    Check log message    ${tc.kws[0].msgs[4]}    critical message    ERROR
    Check log message    ${ERRORS.msgs[0]}    warning message    WARN
    Check log message    ${ERRORS.msgs[1]}    error message    ERROR
    Check log message    ${ERRORS.msgs[2]}    critical message    ERROR

Log with custom levels
    ${tc} =    Check test case    ${TEST NAME}
    Check log message    ${tc.kws[0].msgs[1]}    below debug    TRACE
    Check log message    ${tc.kws[0].msgs[2]}    between debug and info    DEBUG
    Check log message    ${tc.kws[0].msgs[3]}    between info and warning    INFO
    Check log message    ${tc.kws[0].msgs[4]}    between warning and error    WARN
    Check log message    ${tc.kws[0].msgs[5]}    above error    ERROR

Log exception
    ${tc} =    Check test case    ${TEST NAME}
    ${message} =    Catenate    SEPARATOR=\n
    ...    Error occurred!
    ...    Traceback (most recent call last):
    ...    ${SPACE*2}File "*", line 58, in log_exception
    ...    ${SPACE*4}raise ValueError('Bang!')
    ...    ValueError: Bang!
    Check log message    ${tc.kws[0].msgs[0]}    ${message}    ERROR    pattern=True

Messages below threshold level are ignored fully
    ${tc}=    Check test case    ${TEST NAME}
    Should be empty    ${tc.kws[0].msgs}

Error in creating message is logged
    ${tc}=    Check test case    ${TEST NAME}
    Check log message    ${tc.kws[0].msgs[0]}
    ...    Failed to log following message properly: <Unrepresentable object InvalidMessage. Error: Should not have been logged>
    Check log message    ${tc.kws[0].msgs[1]}
    ...    Should not have been logged\nTraceback (most recent call last):*    DEBUG    pattern=true

Log using custom logger
    ${tc} =    Check test case    ${TEST NAME}
    Check log message    ${tc.kws[0].msgs[0]}    custom logger
    Stdout Should Contain    Custom Logger

Log using non-propagating logger
    ${tc} =    Check test case    ${TEST NAME}
    Should be empty    ${tc.kws[0].msgs}
    Stdout Should Contain    Nonprop Logger

Timestamps are accurate
    ${tc} =    Check test case    ${TEST NAME}
    Length Should Be    ${tc.kws[0].msgs}    2
    ${msg1}    ${msg2} =    Set variable    ${tc.kws[0].msgs}
    Check log message    ${msg1}    First message
    Check log message    ${msg2}    Second message 0.1 sec later
    Should be true    '${msg1.timestamp}' < '${msg2.timestamp}'

Logging when timeout is in use
    ${tc} =    Check test case    ${TEST NAME}
    Check log message    ${tc.kws[0].msgs[0]}    Test timeout 5 seconds active. * seconds left.    DEBUG    pattern=yep
    Check log message    ${tc.kws[0].msgs[1]}    something

Suppress errors from logging module
    Stderr Should Contain    Traceback    count=1
