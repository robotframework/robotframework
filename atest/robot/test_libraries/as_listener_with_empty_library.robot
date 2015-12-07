*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    test_libraries/as_listener/empty_library.robot
Resource        atest_resource.robot

*** Test Cases ***
Empty library should not cause warning when it is listener
    Stderr Should Be Equal To    SEPARATOR=\n
    ...     START TEST
    ...     MESSAGE We do nothing
    ...     END TEST
    ...     CLOSE (test)
    ...     CLOSE (suite)\n
    Check Stderr Does Not Contain     WARN
