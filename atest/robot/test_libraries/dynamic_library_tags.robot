*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    test_libraries/dynamic_library_tags.robot
Test Template    Keyword Tags Should Be
Resource         atest_resource.robot

*** Test Cases ***
Tags from documentation
    0    tag1    tag2
    1    tag

Tags from get_keyword_tags
    0    t1    t2    t3

Tags both from doc and get_keyword_tags
    0    1    2    3    4

*** Keywords ***
Keyword Tags Should Be
    [Arguments]    ${index}    @{tags}
    ${tc} =    Check Test Case    ${TESTNAME}
    Lists Should Be Equal    ${tc.kws[${index}].tags}    ${tags}
