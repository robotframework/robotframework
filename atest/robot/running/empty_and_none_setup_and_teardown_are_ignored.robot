*** Settings ***
Suite Setup       Run Tests    ${EMPTY}
...               running/empty_setup_and_teardown_are_ignored.robot running/none_setup_and_teardown_are_ignored.robot
Resource          atest_resource.robot

*** Test Cases ***
Empty suite setup and teardown are ignored
    Should Not Have Setup Or Teardown    ${SUITE.suites[0]}

Empty test setup and teardown are ignored
    Test Should Not Have Setup Or Teardown    Empty default setup and teardown
    Test Should Not Have Setup Or Teardown    Empty custom setup and teardown

None suite setup and teardown are ignored
    Should Not Have Setup Or Teardown    ${SUITE.suites[1]}

None test setup and teardown are ignored
    Test Should Not Have Setup Or Teardown    None default setup and teardown
    Test Should Not Have Setup Or Teardown    None custom setup and teardown

*** Keywords ***
Should Not Have Setup Or Teardown
    [Arguments]    ${item}
    Should Be Equal    ${item.status}    PASS
    Should Be Equal    ${item.keywords.setup}    ${NONE}
    Should Be Equal    ${item.keywords.teardown}    ${NONE}

Test Should Not Have Setup Or Teardown
    [Arguments]    ${name}
    ${tc} =    Check Test Case    ${name}
    Should Not Have Setup Or Teardown    ${tc}
