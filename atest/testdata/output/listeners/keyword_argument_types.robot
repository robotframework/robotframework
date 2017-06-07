*** Settings ***
Metadata       ${1}    ${2}
Library        RunKeywordWithNonStringArguments.py

*** Variables ***
@{ARGS}        Create List    ${1}    ${2}    ${NONE}

*** Test Cases ***
Run Keyword with already resolved non-string arguments in test data
    [Tags]    ${1}    ${2}
    ${result} =    Run Keyword    @{ARGS}
    Should Be Equal    ${result}    ${ARGS[1:]}

Run Keyword with non-string arguments in library
    ${result} =    Run Keyword With Non String Arguments
    Should Be Equal    ${result}    ${ARGS[1:]}
