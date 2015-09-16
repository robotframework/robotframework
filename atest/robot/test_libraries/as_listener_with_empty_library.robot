*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    test_libraries/as_listener/empty_library.robot
Resource        atest_resource.robot

*** Test Cases ***
Empty library should not cause warning when it is listener
    Stderr Should Match
    ...     SEPARATOR=\n
    ...     *START TEST
    ...     MESSAGE Arguments: [ 'We do nothing' ]
    ...     MESSAGE We do nothing
    ...     MESSAGE Return: None
    ...     END TEST
    ...     CLOSE
    Check Stderr Does Not Contain     WARN
