*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/keyword_tags
Resource         atest_resource.robot
Test Template    Keyword tags should be

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
    Error in library    LibraryWithKeywordTags
    ...    Adding keyword 'invalid_library_keyword_tags' failed:
    ...    Expected tags to be list-like, got integer.

User keyword tags with `[Tags]` setting
    first    two words

User keyword tags with `[Tags]` setting containing variables
    3    first    second    Tag    third

User keyword tags with documentation
    3    one    two words

User keyword tags with documentation and setting
    2    3    one    two    two words

User keyword tags with duplicates
    2    first    second    third    XXX

Dynamic library keyword with tags
    bar    foo

Keyword tags setting in resource file
    in resource
    in resource    own    index=1

Keyword tags setting in test case file
    first    second
    first    own    second    index=1

Keyword tags setting in init file

*** Keywords ***
Keyword tags should be
    [Arguments]    @{tags}    ${index}=0
    ${tc}=    Check Test Case    ${TESTNAME}
    Lists should be equal    ${tc.body[${index}].tags}    ${tags}
