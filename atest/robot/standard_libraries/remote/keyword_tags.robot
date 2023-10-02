*** Settings ***
Suite Setup      Run Remote Tests    keyword_tags.robot    keywordtags.py
Test Template    Keyword tags should be
Resource         remote_resource.robot

*** Test Cases ***
No tags
    @{EMPTY}

Doc contains tags only
    bar    foo

Doc contains tags after doc
    are    my    tags    these

Empty 'robot_tags' means no tags
    @{EMPTY}

'robot_tags'
    42    bar    foo

'robot_tags' and doc tags
    bar    foo    zap

*** Keywords ***
Keyword tags should be
    [Arguments]    @{tags}
    ${tc} =    Check Test Case    ${TESTNAME}
    Lists Should Be Equal    ${tc.kws[0].tags}    ${tags}
