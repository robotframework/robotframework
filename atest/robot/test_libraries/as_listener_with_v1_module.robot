*** Settings ***
Suite Setup     Run Tests  ${EMPTY}
...      test_libraries/as_listener/module_v1_listenerlibrary.robot
Resource        atest_resource.robot

*** Test Cases ***
Module listener with v1 version listener api
    Stderr Should Match
    ...     SEPARATOR=\n
    ...     *START TEST Dummy test \ []
    ...     END TEST PASS${SPACE}
    ...     CLOSE
    Check Stderr Does Not Contain     WARN
