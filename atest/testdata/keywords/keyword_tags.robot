*** Settings ***
Library         LibraryWithKeywordTags.py
Library         DynamicLibraryWithKeywordTags.py

*** Variables ***
${TAG}          Tag
@{TAGS}         first    second    third

*** Test Cases ***
Library keyword tags with `robot_tags` attribute
    Library keyword tags with attribute

Library keyword tags with `keyword` decorator
    Library keyword tags with decorator

Library keyword tags with documentation
    Library keyword tags with documentation

Library keyword tags with documentation and attribute
    Library keyword tags with documentation and attribute

Invalid library keyword tags
    [Documentation]    FAIL No keyword with name 'Invalid library keyword tags' found.
    Invalid library keyword tags

User keyword tags with `[Tags]` setting
    User keyword tags with setting

User keyword tags with `[Tags]` setting containing variables
    User keyword tags with setting containing variables

User keyword tags with documentation
    User keyword tags with documentation

User keyword tags with documentation and setting
    User keyword tags with documentation and setting

User keyword tags with duplicates
    User keyword tags with duplicates

Dynamic library keyword with tags
    Dynamic library keyword with tags

*** Keywords ***
User keyword tags with setting
    [Tags]    first    two words
    No Operation

User keyword tags with setting containing variables
    [Tags]    ${TAG}    @{TAGS}    ${3}
    No Operation

User keyword tags with documentation
    [Documentation]    Tags: On non-last line are ignored
    ...    Tags: are ignored also here
    ...    Tags: one, two words, ${3}
    No Operation

User keyword tags with documentation and setting
    [Documentation]    Tags: one, two words, ${3}
    [Tags]    two    ${2}
    No Operation

User keyword tags with duplicates
    [Documentation]    Tags: First, 2, Third, ${2}, xXx, xxx
    [Tags]    first    ${2}    @{TAGS}    FIRST    @{EMPTY}    @{TAGS}    2    XXX
    No Operation
