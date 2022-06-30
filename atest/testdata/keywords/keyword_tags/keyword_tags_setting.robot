*** Settings ***
Keyword Tags        first    second
Resource            keyword_tags_setting.resource

*** Test Cases ***
Keyword tags setting in resource file
    Keyword without own tags in resource
    Keyword with own tags in resource
    Keyword with own tags in documentation in resource

Keyword tags setting in test case file
    Keyword without own tags
    Keyword with own tags
    Keyword with own tags in documentation

*** Keywords ***
Keyword without own tags
    No operation

Keyword with own tags
    [Tags]    own
    No operation

Keyword with own tags in documentation
    [Documentation]    Documentation.
    ...                Tags: in, doc
    No operation
