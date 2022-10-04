*** Settings ***
Documentation     Doc for suite. Not used by Libdoc.
Test Tags         Should not cause errors with Libdoc.
Keyword Tags      keyword tags

*** Test Cases ***
This is a suite file, not a resource file.

*** Keywords ***
1. Example
    [Documentation]    Keyword doc with ${CURDIR}.
    [Tags]    tags

2. Keyword with some "stuff" to <escape>
    [Arguments]    ${a1}    ${a2}=c:\temp\
    [Documentation]   foo bar `kw` & some "stuff" to <escape> .\n\nbaa `${a1}`
    [Tags]    ${CURDIR}

3. Different argument types
    [Arguments]    ${mandatory}    ${optional}=default    @{varargs}
    ...            ${kwo}=default    ${another}    &{kwargs}
    [Documentation]    Multiple
    ...
    ...                lines.

4. Embedded ${arguments}
    [Documentation]    Hyvää yötä. дякую!
