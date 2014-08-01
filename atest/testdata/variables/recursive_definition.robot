*** Settings ***
Test Template     Variable should not exist

*** Variables ***
${VAR}            ${VAR}
${V1}             ${V2}
${V2}             ${V3}
${V3}             ${V1}
${xxx}            ${X X X}
@{LIST}           @{list}
@{L1}             @{L2}
@{L2}             Hello    @{L1}

*** Test Cases ***
Direct recursion
    ${VAR}

Indirect recursion
    ${V1}
    ${V2}
    ${V3}

Case-insensitive recursion
    ${xxx}

Recursive list variable
    @{LIST}
    @{L1}
    @{L2}
