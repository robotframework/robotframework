*** Settings ***
Suite Setup       Run Tests    ${EMPTY}
...               running/empty_setup_and_teardown_are_ignored.robot running/none_setup_and_teardown_are_ignored.robot
Resource          atest_resource.robot

*** Test Cases ***
Empty suite setup and teardown are ignored
    Suite Should Not Have Setup Or Teardown    ${SUITE.suites[0]}

Empty test setup and teardown are ignored
    Test Should Not Have Setup Or Teardown    Empty default setup and teardown
    Test Should Not Have Setup Or Teardown    Empty custom setup and teardown

None suite setup and teardown are ignored
    Suite Should Not Have Setup Or Teardown    ${SUITE.suites[1]}

None test setup and teardown are ignored
    Test Should Not Have Setup Or Teardown    None default setup and teardown
    Test Should Not Have Setup Or Teardown    None custom setup and teardown

*** Keywords ***
Suite Should Not Have Setup Or Teardown
    [Arguments]    ${suite}
    Should Be Equal    ${suite.status}    PASS
    Setup Should Not Be Defined    ${suite}
    Teardown Should Not Be Defined    ${suite}

Test Should Not Have Setup Or Teardown
    [Arguments]    ${name}
    ${tc} =    Check Test Case    ${name}
    Should Be Equal    ${tc.status}    PASS
    Setup Should Not Be Defined     ${tc}
    Teardown Should Not Be Defined     ${tc}
