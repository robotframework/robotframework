*** Setting ***
Suite Setup       Run Tests    --loglevel DEBUG    test_libraries/error_msg_and_details.robot
Force Tags        regression
Default Tags      pybot    jybot
Resource          atest_resource.robot
Test Template     Verify Test Case And Error In Log

*** Test Case ***
Exception Type is Removed From Generic Failures
    Generic Failure    foo != bar

Exception Type is Removed From Generic Java Failures
    [Tags]    jybot
    Generic Failure In Java    bar != foo    2

Exception Type is Removed with Exception Attribute
    Exception Name Suppressed in Error Message    No Exception Name

Exception Type is Removed with Exception Attribute in Java
    [Tags]    jybot
    Exception Name Suppressed in Error Message In Java    No Exception Name

Exception Type is Included In Non-Generic Failures
    Non Generic Failure    FloatingPointError: Too Large A Number !!

Exception Type is Included In Non-Generic Java Failures
    [Tags]    jybot
    Non Generic Failure In Java    ArrayStoreException: My message

Message Is Got Correctly If Python Exception Has Non-String Message
    Python Exception With Non-String Message    ValueError: ['a', 'b', (1, 2), None, {'a': 1}]    1

Message Is Got Correctly If Python Exception Has 'None' Message
    Python Exception With 'None' Message    AssertionError

Multiline Error
    ${TESTNAME}   First line\n2nd\n3rd and last

Multiline Java Error
    [Tags]   jybot
    ${TESTNAME}   ArrayStoreException: First line\n2nd\n3rd and last

Multiline Error With CRLF
    ${TESTNAME}   First line\n2nd\n3rd and last

Message Is Got Correctly If Java Exception Has 'null' Message
    [Tags]    jybot
    Java Exception With 'null' Message    ArrayStoreException

Message And Internal Trace Are Removed From Details When Exception In Library
    [Template]    NONE
    ${tc} =    Verify Test Case And Error In Log    Generic Failure    foo != bar
    Verify Python Traceback    ${tc.kws[0].msgs[1]}    exception    raise exception, msg
    ${tc} =    Verify Test Case And Error In Log    Non Generic Failure    FloatingPointError: Too Large A Number !!
    Verify Python Traceback    ${tc.kws[0].msgs[1]}    exception    raise exception, msg

Message And Internal Trace Are Removed From Details When Exception In Java Library
    [Tags]    jybot
    [Template]    NONE
    ${tc} =    Verify Test Case And Error In Log    Generic Failure In Java    bar != foo    2
    Verify Java Stack Trace    ${tc.kws[2].msgs[1]}    java.lang.AssertionError: \    ExampleJavaLibrary.checkInHashtable
    ${tc} =    Verify Test Case And Error In Log    Non Generic Failure In Java    ArrayStoreException: My message
    Verify Java Stack Trace    ${tc.kws[0].msgs[1]}    java.lang.ArrayStoreException: \    ExampleJavaLibrary.exception    ExampleJavaLibrary.javaException

Message and Internal Trace Are Removed From Details When Exception In External Code
    [Template]    NONE
    ${tc} =    Verify Test Case And Error In Log    External Failure    UnboundLocalError: Raised from an external object!
    Verify Python Traceback    ${tc.kws[0].msgs[1]}    external_exception    ObjectToReturn('failure').exception(name, msg)    exception    raise exception, msg

Message and Internal Trace Are Removed From Details When Exception In External Java Code
    [Tags]    jybot
    [Template]    NONE
    ${tc} =    Verify Test Case And Error In Log    External Failure In Java    IllegalArgumentException: Illegal initial capacity: -1
    Verify Java Stack Trace    ${tc.kws[0].msgs[1]}    java.lang.IllegalArgumentException: \    java.util.HashMap.    java.util.HashMap.    JavaObject.exception    ExampleJavaLibrary

No Details For Timeouts
    [Template]    Verify Test Case, Error In Log And No Details
    Timeout Expires    Test timeout 200 milliseconds exceeded.    ${1}

No Details For Non Existing Keywords
    [Template]    Verify Test Case, Error In Log And No Details
    Non existing Keyword    No keyword with name 'Non Existing Keyword' found.

No Details For Non Existing Variables
    [Template]    Verify Test Case, Error In Log And No Details
    Non Existing Scalar Variable    Non-existing variable '\${non existing}'.
    Non Existing List Variable    Non-existing variable '\@{non existing}'.

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
    [Arguments]    ${msg}    @{funtions_and_texts}
    ${exp} =    Set Variable    Traceback \\(most recent call last\\):
    @{funtions_and_texts} =    Regexp Escape    @{funtions_and_texts}
    : FOR    ${func}    ${text}    IN    @{funtions_and_texts}
    \    ${exp} =    Set Variable    ${exp}\n \\s+File ".*", line \\d+, in ${func}\n \\s+${text}
    Should Match Regexp    ${msg.message}    ${exp}
    Should Be Equal    ${msg.level}    DEBUG

Verify Java Stack Trace
    [Arguments]    ${msg}    ${exception}    @{functions}
    ${exp} =    Regexp Escape    ${exception}
    : FOR    ${func}    IN    @{functions}
    \    ${func} =    Regexp Escape    ${func}
    \    ${exp} =    Set Variable    ${exp}\n \\s+at ${func}.+
    Should Match Regexp    ${msg.message}    ${exp}
    Should Be Equal    ${msg.level}    DEBUG

