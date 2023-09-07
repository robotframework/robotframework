*** Settings ***
Suite Setup       Run Tests
...               --exclude exclude -e e2 --include include_this_test --skip skip_me --skiponfailure sof
...               variables/automatic_variables/
Resource          atest_resource.robot

*** Test Cases ***
Previous Test Variables Should Have Default Values
    Check test case    ${TEST NAME}

Test Name
    Check Test Case    ${TEST NAME}

Test Documentation
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.doc}    My doc.\nIn 2 lines! And with variable value!!

Test Tags
    Check Test Tags    ${TEST NAME}    Force 1    Hello, world!    id-42    include this test    variable value

Modifying \${TEST TAGS} does not affect actual tags test has
    Check Test Tags    ${TEST NAME}    Force 1    mytag    include this test

Suite Name
    Check Test Case    ${TEST NAME}

Suite Documentation
    Check Test Case    ${TEST NAME}
    Should Be Equal    ${SUITE.suites[0].doc}    This is suite documentation. With variable value.

Suite Metadata
    Check Test Case    ${TEST NAME}
    Should Be Equal    ${SUITE.suites[0].metadata['Meta2']}    variable value

Modifying \&{SUITE METADATA} does not affect actual metadata suite has
    Check Test Case    ${TEST NAME}
    Should Be Equal    ${SUITE.suites[0].metadata['MeTa1']}    Value
    Dictionary Should Not Contain Key    ${SUITE.suites[0].metadata}    NotSet

Suite Status And Suite Message Are Not Visible In Tests
    Check Test Case    ${TEST NAME}

Suite Variables Are Available At Import Time
    [Documentation]    Possible variables in them are not resolved, though.
    Check Test Case    ${TEST NAME}

Test Status Should Not Exist Outside Teardown
    Check test case    ${TEST NAME}

Test Message Should Not Exist Outside Teardown
    Check test case    ${TEST NAME}

Test Status When Test Fails
    Check test case    ${TEST NAME}

Test Status When Setup Fails
    Check test case    ${TEST NAME}

Previous Test Variables Should Have Correct Values When That Test Fails
    Check test case    ${TEST NAME}

Previous Test Variables Should Have Default Values From Previous Suite
    Check test case    ${TEST NAME}

Suite And Prev Test Variables Work Correctly In Setup
    Should Be Equal    ${SUITE.suites[0].setup.status}    PASS
    Should Be Equal    ${SUITE.suites[1].setup.status}    PASS

Suite And Prev Test Variables Work Correctly In Teardown
    Should Be Equal    ${SUITE.suites[0].teardown.status}    PASS
    Should Be Equal    ${SUITE.suites[1].teardown.status}    PASS

\&{OPTIONS}
    Check Test Case    ${TEST NAME}
