*** Settings ***
Test Template     Variable should not exist
Resource          ${IMPORT 1}.robot
Library           ${IMPORT 2}.py

*** Variables ***
${DIRECT}         ${DIRECT}
${VAR 1}          ${VAR 2}
${VAR 2}          ${VAR 3}
${VAR 3}          ${VAR 1}
${xxx}            ${X X X}
@{LIST}           @{list}
@{LIST 1}         @{LIST 2}
@{LIST 2}         Hello    @{LIST 1}
${IMPORT 1}       ${IMPORT 2}
${IMPORT 2}       ${IMPORT 1}

*** Test Cases ***
Direct recursion
    ${DIRECT}

Indirect recursion
    ${VAR 1}
    ${VAR 2}
    ${VAR 3}

Case-insensitive recursion
    ${xxx}

Recursive list variable
    @{LIST}
    @{LIST 1}
    @{LIST 2}

Recursion with variables used in imports
    ${IMPORT 1}
    ${IMPORT 2}
