*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/deprecated_builtin/verify.robot
Resource          atest_resource.robot

*** Test Case ***
Error
    Check testcase    Error

Error With Message
    Check testcase    Error With Message

Fail If 1
    Check testcase    Fail If 1

Fail If 2
    Check testcase    Fail If 2

Fail Unless 1
    Check testcase    Fail Unless 1

Fail Unless 2
    Check testcase    Fail Unless 2

Fail If Equal
    Check testcase    Fail If Equal

Fail Unless Equal
    Check testcase    Fail Unless Equal

Fail If Ints Equal
    Check testcase    Fail If Ints Equal

Fail Unless Ints Equal
    Check testcase    Fail Unless Ints Equal

Fail If Floats Equal
    Check testcase    Fail If Floats Equal

Fail Unless Floats Equal
    Check testcase    Fail Unless Floats Equal

Fail If Starts
    Check testcase    Fail If Starts

Fail Unless Starts
    Check testcase    Fail Unless Starts

Fail If Ends
    Check testcase    Fail If Ends

Fail Unless Ends
    Check testcase    Fail Unless Ends

Fail If Contains
    Check testcase    Fail If Contains

Fail Unless Contains
    Check testcase    Fail Unless Contains

Fail If Matches
    Check testcase    Fail If Matches

Fail Unless Matches
    Check testcase    Fail Unless Matches

Fail If Regexp Matches
    Check testcase    Fail If Regexp Matches

Fail Unless Regexp Matches
    Check testcase    Fail Unless Regexp Matches
