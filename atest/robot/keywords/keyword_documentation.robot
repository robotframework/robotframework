*** Settings ***
Documentation    Testing documentation of static library keywords.
...
...              Documentation of other keywords is tested elsewhere:
...              - Dynamic keywords: test_libraries/dynamic_library_args_and_docs.robot
...              - User keywords: parsing/user_keyword_settings.robot

Suite Setup      Run Tests    ${EMPTY}    keywords/keyword_documentation.robot
Test Template    Verify Documentation
Resource         atest_resource.robot

*** Test Cases ***
No documentation
    ${EMPTY}

One line documentation
    One line doc

Multiline documentation
    First line is short doc.

Multiline documentation with split short doc
    Short doc can be split into\nmultiple\nphysical\nlines.

*** Keywords ***
Verify Documentation
    [Arguments]    ${doc}    ${test}=${TEST NAME}
    ${tc} =    Check Test Case    ${test}
    Should Be Equal    ${tc.kws[0].doc}    ${doc}
