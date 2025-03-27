*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/custom_dir.robot
Resource          atest_resource.robot

*** Test Cases ***
Normal keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    ARG

Keyword implemented via getattr
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    ARG

Failure in getattr is handled gracefully
    Adding keyword failed    via_getattr_invalid    ValueError: This is invalid!

Non-existing attribute is handled gracefully
    Adding keyword failed    non_existing    AttributeError: 'non_existing' does not exist.

*** Keywords ***
Adding keyword failed
    [Arguments]    ${name}    ${error}
    Syslog should contain    In library 'CustomDir': Adding keyword '${name}' failed: ${error}
