*** Settings ***
Library           DupeHybridKeywords.py

*** Variables ***
${INDENT}         ${SPACE * 4}

*** Test Cases ***
Using keyword defined multiple times fails
    [Documentation]    FAIL Keyword with same name defined multiple times.
    Defined TWICE

Keyword with embedded arguments defined multiple times fails at run-time
    [Documentation]    FAIL
    ...    Multiple keywords matching name 'Embedded twice' found:
    ...    ${INDENT}DupeHybridKeywords.EMBEDDED \${ARG}
    ...    ${INDENT}DupeHybridKeywords.Embedded \${twice}
    Embedded twice

Exact duplicate is accepted
    Exact dupe is OK
