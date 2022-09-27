*** Test Cases ***
Matching arguments
    [Documentation]    FAIL 4 != 5
    [Template]    The result of ${calculation} should be ${expected}
    1 + 1    2
    1 + 2    3
    1 + 3    5

Argument names do not need to be same as in definition
    [Documentation]    FAIL 4 != 5
    [Template]    The result of ${foo} should be ${bar}
    1 + 1    2
    1 + 2    3
    1 + 3    5

Some arguments can be hard-coded
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) 2 != 3
    ...
    ...    2) 4 != 3
    [Template]    The result of ${expression} should be 3
    1 + 1
    1 + 2
    1 + 3

Can have different arguments than definition
    [Documentation]    FAIL No keyword with name 'The non-existing of 666 should be 42' found.
    [Template]    The ${meaning} of ${life} should be 42
    result    38 + 3 + 1
    non-existing    666

Can use variables
    [Template]    The result of ${calculation} should be ${expected}
    ${1} + ${2}    ${3}

Cannot have more arguments than variables
    [Documentation]    FAIL
    ...    Keyword 'The result of \${calculation} should be \${expected}' expected 0 arguments, got 2.
    [Template]    The result of ${calc} should be 3
    1 + 2    extra

Cannot have less arguments than variables
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Keyword 'The result of \${calculation} should be \${expected}' expected 0 arguments, got 1.
    ...
    ...    2) Keyword 'The result of \${calculation} should be \${expected}' expected 0 arguments, got 1.
    [Template]    The result of ${calc} should be ${extra}
    1 + 2
    4 - 1

*** Keywords ***
The result of ${calculation} should be ${expected}
    ${result} =    Evaluate    ${calculation}
    Should Be Equal As Integers   ${result}    ${expected}
