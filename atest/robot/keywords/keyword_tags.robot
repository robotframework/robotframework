*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/keyword_tags.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot
Test template    Keyword tags should be

*** Test Cases ***
Library keyword tags with `robot_tags` attribute
    first    second

Library keyword tags with `keyword` decorator
    2    one

Library keyword tags with documentation
    [Tags]    not ready
    one    two words

Invalid library keyword tags
    [Tags]    not ready
    [Template]    NONE
    Check Test Case    ${TESTNAME}
    Check log message    ${ERRORS[0]}
    ...    Adding keyword 'Invalid library keyword tags' to library 'LibraryWithKeywordTags' failed: DataError: xxxxx
    ...    level=ERROR

User keyword tags with `[Tags]` setting
    2    first

User keyword tags with documentation
    [Tags]    not ready
    3    one    two words

*** Keywords ***
Keyword tags should be
    [Arguments]    @{tags}
    ${tc}=    Check Test Case    ${TESTNAME}
    Lists should be equal    ${tc.kws[0].tags}    ${tags}
