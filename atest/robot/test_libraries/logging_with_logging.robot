*** Settings ***
Documentation     Tests for logging using Python's `logging` module.
Suite Setup       Run Tests    -L none    test_libraries/logging_with_logging.robot
Resource          atest_resource.robot

*** Test Cases ***
All logging is disabled
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc[0].messages}
    Should Be Empty    ${tc[1].messages}

Log with default levels
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}     debug message       DEBUG
    Check Log Message    ${tc[0, 1]}     info message        INFO
    Check Log Message    ${tc[0, 2]}     warning message     WARN
    Check Log Message    ${tc[0, 3]}     error message       ERROR
    Check Log Message    ${tc[0, 4]}     critical message    ERROR
    Check Log Message    ${ERRORS[0]}    warning message     WARN
    Check Log Message    ${ERRORS[1]}    error message       ERROR
    Check Log Message    ${ERRORS[2]}    critical message    ERROR

Log with custom levels
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 1]}    below debug                  TRACE
    Check Log Message    ${tc[0, 2]}    between debug and info       DEBUG
    Check Log Message    ${tc[0, 3]}    between info and warning     INFO
    Check Log Message    ${tc[0, 4]}    between warning and error    WARN
    Check Log Message    ${tc[0, 5]}    above error                  ERROR

Log exception
    ${tc} =    Check Test Case    ${TEST NAME}
    ${message} =    Catenate    SEPARATOR=\n
    ...    Error occurred!
    ...    Traceback (most recent call last):
    ...    ${SPACE*2}File "*", line 56, in log_exception
    ...    ${SPACE*4}raise ValueError('Bang!')
    ...    ValueError: Bang!
    Check Log Message    ${tc[0, 0]}    ${message}    ERROR    pattern=True    traceback=True

Messages below threshold level are ignored fully
    ${tc}=    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc[0].messages}

Error in creating message is logged
    ${tc}=    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}
    ...    Failed to log following message properly: <Unrepresentable object InvalidMessage. Error: Should not have been logged>
    Check Log Message    ${tc[0, 1]}
    ...    Should not have been logged\nTraceback (most recent call last):*    DEBUG    pattern=True

Log using custom logger
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}    custom logger
    Stdout Should Contain    Custom Logger

Log using non-propagating logger
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc[0].messages}
    Stdout Should Contain    Nonprop Logger

Timestamps are accurate
    ${tc} =    Check Test Case    ${TEST NAME}
    Length Should Be    ${tc[0].messages}    2
    ${msg1}    ${msg2} =    Set Variable    ${tc[0].messages}
    Check Log Message    ${msg1}    First message
    Check Log Message    ${msg2}    Second message 0.1 sec later
    Should Be True    '${msg1.timestamp}' < '${msg2.timestamp}'

Logging when timeout is in use
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}    Test timeout 5 seconds active. * seconds left.    DEBUG    pattern=True
    Check Log Message    ${tc[0, 1]}    something

Suppress errors from logging module
    Stderr Should Contain    Traceback    count=1

Log with format
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}    root INFO logged at info

Log non-strings
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}    42
    Check Log Message    ${tc[0, 1]}    True
    Check Log Message    ${tc[0, 2]}    None
