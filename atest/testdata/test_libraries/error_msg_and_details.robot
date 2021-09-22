*** Setting ***
Library           ExampleLibrary
Library           nön_äscii_dïr/valid.py

*** Test Case ***
Generic Failure
    [Documentation]    FAIL foo != bar
    Exception    AssertionError    foo != bar

Exception Name Suppressed in Error Message
    [Documentation]    FAIL No Exception Name
    Fail with suppressed exception name    No Exception Name

Non Generic Failure
    [Documentation]    FAIL FloatingPointError: Too Large A Number !!
    Exception    FloatingPointError    Too Large A Number !!

Python Exception With Non-String Message
    [Documentation]    FAIL ValueError: ['a', 'b', (1, 2), None, {'a': 1}]
    ${msg} =    Evaluate    ['a', 'b', (1, 2), None, {'a': 1}]
    Exception    ValueError    ${msg}

Python Exception With 'None' Message
    [Documentation]    FAIL None
    Exception    AssertionError    ${None}

Generic Python class
    [Documentation]    FAIL RuntimeError
    Exception    RuntimeError    class_only=True

Non-Generic Python class
    [Documentation]    FAIL ZeroDivisionError
    Exception    ZeroDivisionError    class_only=True

Multiline Error
    [Documentation]    FAIL First line\n2nd\n3rd and last
    Exception    AssertionError    First line\n2nd\n3rd and last

Multiline Error With CRLF
    [Documentation]    FAIL First line\n2nd\n3rd and last
    Exception    AssertionError    First line\r\n2nd\r\n3rd and last

External Failure
    [Documentation]    FAIL UnboundLocalError: Raised from an external object!
    External Exception    UnboundLocalError    Raised from an external object!

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
