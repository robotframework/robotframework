*** Setting ***
Suite Setup       Run Tests    --loglevel DEBUG    test_libraries/error_msg_and_details.robot
Resource          atest_resource.robot
Test Template     Verify Test Case And Error In Log

*** Test Case ***
Exception Type is Removed From Generic Failures
    Generic Failure    foo != bar

Exception Type is Removed with Exception Attribute
    Exception Name Suppressed in Error Message    No Exception Name

Exception Type is Included In Non-Generic Failures
    Non Generic Failure    FloatingPointError: Too Large A Number !!

Message Contains Only Class Name When Raising Only Class
    Generic Python class    RuntimeError
    Non-Generic Python class    ZeroDivisionError

Message Is Got Correctly If Python Exception Has Non-String Message
    Python Exception With Non-String Message    ValueError: ['a', 'b', (1, 2), None, {'a': 1}]    1

Message Is Got Correctly If Python Exception Has 'None' Message
    Python Exception With 'None' Message    None

Multiline Error
    ${TESTNAME}   First line\n2nd\n3rd and last

Multiline Error With CRLF
    ${TESTNAME}   First line\n2nd\n3rd and last

Message And Internal Trace Are Removed From Details When Exception In Library
    [Template]    NONE
    ${tc} =    Verify Test Case And Error In Log    Generic Failure    foo != bar
    Verify Python Traceback    ${tc.kws[0].msgs[1]}
    ...    ../testresources/testlibs/ExampleLibrary.py
    ...    exception
    ...    raise exception(msg)
    ${tc} =    Verify Test Case And Error In Log    Non Generic Failure    FloatingPointError: Too Large A Number !!
    Verify Python Traceback    ${tc.kws[0].msgs[1]}
    ...    ../testresources/testlibs/ExampleLibrary.py
    ...    exception
    ...    raise exception(msg)

Message and Internal Trace Are Removed From Details When Exception In External Code
    [Template]    NONE
    ${tc} =    Verify Test Case And Error In Log    External Failure    UnboundLocalError: Raised from an external object!
    Verify Python Traceback    ${tc.kws[0].msgs[1]}
    ...    ../testresources/testlibs/ExampleLibrary.py
    ...    external_exception
    ...    ObjectToReturn('failure').exception(name, msg)
    ...    ../testresources/testlibs/objecttoreturn.py
    ...    exception
    ...    raise exception(msg)

Failure in library in non-ASCII directory
    [Template]    NONE
    ${tc} =    Verify Test Case And Error In Log    ${TEST NAME}    Keyword in 'nön_äscii_dïr' fails!    index=1
    Verify Python Traceback    ${tc.kws[1].msgs[1]}
    ...    test_libraries/nön_äscii_dïr/valid.py
    ...    failing_keyword_in_non_ascii_dir
    ...    raise AssertionError("Keyword in 'nön_äscii_dïr' fails!")

No Details For Timeouts
    [Template]    Verify Test Case, Error In Log And No Details
    Timeout Expires    Test timeout 200 milliseconds exceeded.    ${1}

No Details For Non Existing Keywords
    [Template]    Verify Test Case, Error In Log And No Details
    Non existing Keyword    No keyword with name 'Non Existing Keyword' found.

No Details For Non Existing Variables
    [Template]    Verify Test Case, Error In Log And No Details
    Non Existing Scalar Variable    Variable '\${non existing}' not found.
    Non Existing List Variable    Variable '\@{non existing}' not found.

Include internal traces when ROBOT_INTERNAL_TRACE is set
    [Template]    NONE
    Set Environment Variable    ROBOT_INTERNAL_TRACES    show, please
    Run Tests    -L DEBUG -t "Generic Failure"    test_libraries/error_msg_and_details.robot
    ${tc} =    Check Test Case    Generic Failure
    ${tb} =    Set Variable    ${tc.kws[0].msgs[1].message}
    Should Start With    ${tb}    Traceback (most recent call last):
    Should End With    ${tb}    raise exception(msg)
    Should Be True    len($tb.splitlines()) > 5
    [Teardown]    Remove Environment Variable    ROBOT_INTERNAL_TRACES

*** Keyword ***
Verify Test Case And Error In Log
    [Arguments]    ${name}    ${error}    ${index}=0    ${msg}=0
    ${tc} =    Check Test Case    ${name}
    Check Log Message    ${tc.kws[${index}].msgs[${msg}]}    ${error}    FAIL
    [Return]    ${tc}

Verify Test Case, Error In Log And No Details
    [Arguments]    ${name}    ${error}    ${msg_index}=${0}
    ${tc} =    Verify Test Case And Error In Log    ${name}    ${error}    0    ${msg_index}
    Length Should Be    ${tc.kws[0].msgs}    ${msg_index + 1}

Verify Python Traceback
    [Arguments]    ${msg}    @{entries}
    ${exp} =    Set Variable    Traceback \\(most recent call last\\):
    FOR    ${path}    ${func}    ${text}    IN    @{entries}
        ${path} =    Normalize Path    ${DATADIR}/${path}
        ${path}    ${func}    ${text} =    Regexp Escape    ${path}    ${func}    ${text}
        ${exp} =    Set Variable    ${exp}\n\\s+File ".*${path}.*", line \\d+, in ${func}\n\\s+${text}
    END
    Should Match Regexp    ${msg.message}    ${exp}
    Should Be Equal    ${msg.level}    DEBUG
