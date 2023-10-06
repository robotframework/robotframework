*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    test_libraries/error_msg_and_details.robot
Resource          atest_resource.robot
Test Template     Verify Test Case And Error In Log

*** Test Cases ***
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
    Traceback Should Be    ${tc.kws[0].msgs[1]}
    ...    ../testresources/testlibs/ExampleLibrary.py    exception    raise exception(msg)
    ...    error=AssertionError: foo != bar
    ${tc} =    Verify Test Case And Error In Log    Non Generic Failure    FloatingPointError: Too Large A Number !!
    Traceback Should Be    ${tc.kws[0].msgs[1]}
    ...    ../testresources/testlibs/ExampleLibrary.py    exception    raise exception(msg)
    ...    error=FloatingPointError: Too Large A Number !!

Message and Internal Trace Are Removed From Details When Exception In External Code
    [Template]    NONE
    ${tc} =    Verify Test Case And Error In Log    External Failure    UnboundLocalError: Raised from an external object!
    Traceback Should Be    ${tc.kws[0].msgs[1]}
    ...    ../testresources/testlibs/ExampleLibrary.py    external_exception    ObjectToReturn('failure').exception(name, msg)
    ...    ../testresources/testlibs/objecttoreturn.py    exception             raise exception(msg)
    ...    error=UnboundLocalError: Raised from an external object!

Chained exceptions
    [Template]    NONE
    # Executed keyword formats exception traceback using `traceback.format_exception()`
    # and logs it so that we can validate the traceback logged by Robot based on it.
    # This avois the need to construct long and complicated tracebacks that are subject
    # change between Python versions.
    ${tc} =    Verify Test Case And Error In Log    Implicitly chained exception    NameError: name 'ooops' is not defined    msg=1
    Check Log Message    ${tc.kws[0].msgs[2]}    ${tc.kws[0].msgs[0].message}    DEBUG
    ${tc} =    Verify Test Case And Error In Log    Explicitly chained exception    Expected error    msg=1
    Check Log Message    ${tc.kws[0].msgs[2]}    ${tc.kws[0].msgs[0].message}    DEBUG

Failure in library in non-ASCII directory
    [Template]    NONE
    ${tc} =    Verify Test Case And Error In Log    ${TEST NAME}    Keyword in 'nön_äscii_dïr' fails!    index=1
    Traceback Should Be    ${tc.kws[1].msgs[1]}
    ...    test_libraries/nön_äscii_dïr/valid.py    failing_keyword_in_non_ascii_dir    raise AssertionError("Keyword in 'nön_äscii_dïr' fails!")
    ...    error=AssertionError: Keyword in 'nön_äscii_dïr' fails!

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
    # Remove '^^^' lines added by Python 3.11+.
    ${tb} =    Evaluate    '\\n'.join(line for line in $tc.kws[0].msgs[1].message.splitlines() if line.strip('^ '))
    Should Start With    ${tb}    Traceback (most recent call last):
    Should Contain       ${tb}    librarykeywordrunner.py
    Should End With      ${tb}    raise exception(msg)\nAssertionError: foo != bar
    Should Be True       len($tb.splitlines()) > 5
    [Teardown]    Remove Environment Variable    ROBOT_INTERNAL_TRACES

*** Keywords ***
Verify Test Case And Error In Log
    [Arguments]    ${name}    ${error}    ${index}=0    ${msg}=0
    ${tc} =    Check Test Case    ${name}
    Check Log Message    ${tc.kws[${index}].msgs[${msg}]}    ${error}    FAIL
    RETURN    ${tc}

Verify Test Case, Error In Log And No Details
    [Arguments]    ${name}    ${error}    ${msg_index}=${0}
    ${tc} =    Verify Test Case And Error In Log    ${name}    ${error}    0    ${msg_index}
    Length Should Be    ${tc.kws[0].msgs}    ${msg_index + 1}
