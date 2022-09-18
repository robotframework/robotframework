*** Settings ***
Documentation        Testing Run Keywords when used with AND. Tests without AND are in
...                  run_keywords.robot.

*** Variables ***
${NOOP}              No Operation
@{MANY ARGUMENTS}    hello    1    2    3
@{ESCAPED}           1    \AND    2    Log Many    x\${escaped}    c:\\temp
@{LIST VARIABLE}     Log Many    this    AND    that
${AND VARIABLE}      AND

*** Test Cases ***
With arguments
    Run Keywords
    ...    Should Be Equal    2    2           AND
    ...    No Operation                        AND
    ...    Log Many    hello    1    2    3    AND
    ...    Should Be Equal    1    1

Should fail with failing keyword
    [Documentation]    FAIL  1 != 2
    Run Keywords    No Operation    AND    Should Be Equal    1    2    AND    Not Executed

Should support keywords and arguments from variables
    Run Keywords
    ...    Should Be Equal   2    2         AND
    ...    ${NOOP}                          AND
    ...    Log Many    @{MANY ARGUMENTS}    AND
    ...    @{EMPTY}    Should Be Equal As Integers    ${1}    @{EMPTY}    1

AND must be upper case
    [Documentation]    FAIL  No keyword with name 'no kw' found.
    Run Keywords    Log Many    this    and    that    AND    no kw

AND must be whitespace sensitive
    [Documentation]    FAIL  No keyword with name 'no kw' found.
    Run Keywords    Log Many    this    A ND    that    AND    no kw

Escaped AND
    [Documentation]    FAIL  No keyword with name 'no kw' found.
    Run Keywords    Log Many    this    \AND    that    AND    no kw

AND from Variable
    [Documentation]    FAIL  No keyword with name 'no kw' found.
    Run Keywords    Log Many    this    ${AND VARIABLE}    that    AND    no kw

AND in List Variable
    [Documentation]    FAIL  No keyword with name 'no kw' found.
    Run Keywords    @{LIST VARIABLE}    AND    no kw

Escapes in List Variable should be handled correctly
    [Documentation]    FAIL  No keyword with name 'no kw' found.
    Run Keywords    Log Many    @{ESCAPED}    AND    no kw

AND as last argument should raise an error
    [Documentation]    FAIL  AND must have keyword before and after.
    Run Keywords    Log Many    1    2    AND    No Operation    AND

Consecutive AND's
    [Documentation]    FAIL  AND must have keyword before and after.
    Run Keywords    Log Many    1    2    AND    AND    No Operation

AND as first argument should raise an error
    [Documentation]    FAIL  AND must have keyword before and after.
    Run Keywords    AND    Log Many    1    2

Keywords names needing escaping
    Run keywords    Needs \\escaping \\\${notvar}    AND    Needs \\escaping \\\${notvar}

Keywords names needing escaping as variable
    @{names} =    Create List    Needs \\escaping \\\${notvar}
    Run keywords    @{names}    AND    ${names}[0]

In test teardown with non-existing variable in keyword name
    [Documentation]
    ...    FAIL Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) No keyword with name '\${bad}' found.
    ...
    ...    2) Executed
    ...
    ...    3) Variable '\${bad}' not found.
    ...
    ...    4) Executed
    No Operation
    [Teardown]    Run keywords
    ...    ${bad}                     AND
    ...    ${{'Fail'}}    Executed    AND
    ...    Embedded ${bad}            AND
    ...    Fail    Executed

*** Keywords ***
Embedded ${arg}
    Log    ${arg}

Needs \escaping \${notvar}
    No operation
