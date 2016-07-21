*** Settings ***
Suite Setup     Run Tests    --pythonpath ${DATADIR}/test_libraries/as_listener    test_libraries/as_listener/import_library.robot
Resource        atest_resource.robot

*** Test Cases ***
Import Library works
    Check Test Case    ${TESTNAME}

Reload Library works
    Check Test Case    ${TESTNAME}
