*** Settings ***
Suite Setup     Run Tests  ${EMPTY}    test_libraries/as_listener/import_library.robot
Force Tags      regression
Resource        atest_resource.robot

*** Test Cases ***
Import Library works
    Check Test Case  ${TESTNAME}
