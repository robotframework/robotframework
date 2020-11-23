*** Setting ***
Library           ExampleLibrary
Library           ExampleJavaLibrary
Library           nön_äscii_dïr/valid.py

*** Test Case ***
Generic Failure
    [Documentation]    FAIL foo != bar
    Exception    AssertionError    foo != bar

Generic Failure In Java
    [Documentation]    FAIL bar != foo
    ${ht} =    Get Hashtable
    Set To Hashtable    ${ht}    foo    bar
    Check In Hashtable    ${ht}    foo    foo

Exception Name Suppressed in Error Message
    [Documentation]    FAIL No Exception Name
    Fail with suppressed exception name    No Exception Name

Non Generic Failure
    [Documentation]    FAIL FloatingPointError: Too Large A Number !!
    Exception    FloatingPointError    Too Large A Number !!

Non Generic Failure In Java
    [Documentation]    FAIL ArrayStoreException: My message
    Java Exception    My message

Exception Name Suppressed in Error Message In Java
    [Documentation]    FAIL No Exception Name
    Fail with suppressed exception name in Java    No Exception Name

Python Exception With Non-String Message
    [Documentation]    FAIL ValueError: ['a', 'b', (1, 2), None, {'a': 1}]
    ${msg} =    Evaluate    ['a', 'b', (1, 2), None, {'a': 1}]
    Exception    ValueError    ${msg}

Python Exception With 'None' Message
    [Documentation]    FAIL None
    Exception    AssertionError    ${None}

Java Exception With 'null' Message
    [Documentation]    FAIL ArrayStoreException
    Java Exception

Generic Python class
    [Documentation]    FAIL RuntimeError
    Exception    RuntimeError    class_only=True

Non-Generic Python class
    [Documentation]    FAIL ZeroDivisionError
    Exception    ZeroDivisionError    class_only=True

Multiline Error
    [Documentation]    FAIL First line\n2nd\n3rd and last
    Exception    AssertionError    First line\n2nd\n3rd and last

Multiline Java Error
    [Documentation]    FAIL ArrayStoreException: First line\n2nd\n3rd and last
    Java Exception    First line\n2nd\n3rd and last

Multiline Error With CRLF
    [Documentation]    FAIL First line\n2nd\n3rd and last
    Exception    AssertionError    First line\r\n2nd\r\n3rd and last

External Failure
    [Documentation]    FAIL UnboundLocalError: Raised from an external object!
    External Exception    UnboundLocalError    Raised from an external object!

External failure in Java
    [Documentation]    FAIL IllegalArgumentException: Illegal initial capacity: -1
    External Java Exception

Failure in library in non-ASCII directory
    [Documentation]    FAIL Keyword in 'nön_äscii_dïr' fails!
    Keyword in non ascii dir
    Failing keyword in non ascii dir

Timeout Expires
    [Documentation]    FAIL Test timeout 200 milliseconds exceeded.
    [Timeout]    200 ms
    Sleep    1

Non existing Keyword
    [Documentation]    FAIL No keyword with name 'Non Existing Keyword' found.
    Non Existing Keyword

Non Existing Scalar Variable
    [Documentation]    FAIL Variable '\${non existing}' not found.
    Log    ${non existing}

Non Existing List Variable
    [Documentation]    FAIL Variable '\@{non existing}' not found.
    Log Many    @{non existing}.
