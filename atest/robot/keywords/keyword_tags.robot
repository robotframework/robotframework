*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/keyword_tags.robot
Resource         atest_resource.robot
Test template    Keyword tags should be

*** Test Cases ***
Library keyword tags with `robot_tags` attribute
    first    second

Library keyword tags with `keyword` decorator
    2    one

Library keyword tags with documentation
    one    two words

Library keyword tags with documentation and attribute
    2    one    two words

Invalid library keyword tags
    [Template]    NONE
    Check Test Case    ${TESTNAME}
    Check log message    ${ERRORS[0]}
    ...    Adding keyword 'invalid_library_keyword_tags' to library 'LibraryWithKeywordTags' failed: Expected tags to list like, got integer.
    ...    level=ERROR

User keyword tags with `[Tags]` setting
    2    first

User keyword tags with documentation
    3    one    two words

User keyword tags with documentation and setting
    2    3    one    two words

Dynamic library keyword with tags
    bar    foo

*** Keywords ***
Keyword tags should be
    [Arguments]    @{tags}
    ${tc}=    Check Test Case    ${TESTNAME}
    Lists should be equal    ${tc.kws[0].tags}    ${tags}
