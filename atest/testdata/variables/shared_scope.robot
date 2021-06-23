*** Settings ***
Variables    scalar_lists.py

*** Variables ***
@{VARIABLE}    list    values
@{LIST2}       spam   eggs     ${21}

*** Test Cases ***
List can overwrite scalar
    ${foo}=    Set variable   scalar
    @{foo}=    Create list    @{VARIABLE}
    Should be equal    ${foo}      ${VARIABLE}

Scalar can overwrite list
    [Documentation]    FAIL Value of variable '\@{VARIABLE}' is not list or list-like.
    ${variable}=    Set variable   scalar
    Log Many    @{VARIABLE}

Variables from file
    Should be equal    ${LIST}       ${LIST2}
    Should be equal    ${LIST}[0]    spam
    @{list}=           Create list    @{VARIABLE}
    Should be equal    ${list}      ${VARIABLE}
