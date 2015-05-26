*** Settings ***
Library        LibraryWithKeywordTags.py

*** Test Cases ***
Library keyword tags with `robot_tags` attribute
    Library keyword tags with attribute

Library keyword tags with `keyword` decorator
    Library keyword tags with decorator

Library keyword tags with documentation
    Library keyword tags with documentation

Invalid library keyword tags
    [Documentation]    FAIL No keyword with name 'Invalid library keyword tags' found.
    Invalid library keyword tags

User keyword tags with `[Tags]` setting
    User keyword tags with setting

User keyword tags with documentation
    User keyword tags with documentation

*** Keywords ***
User keyword tags with setting
    [Tags]    first    ${2}
    No Operation

User keyword tags with documentation
    [Documentation]    Tags: On non-last line are ignored
    ...    Tags: are ignored also here
    ...    Tags: one, two words, ${3}
    No Operation
