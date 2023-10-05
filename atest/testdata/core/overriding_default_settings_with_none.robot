*** Settings ***
Test Setup  Log  Default Setup
Test Teardown  Log  Default Teardown
Test Template  Log
Test Timeout   100 ms
Default Tags   d1  d2

*** Test Cases ***
Overriding Test Setup
    [Setup]  NONE
    [Timeout]  NONE
    ${TEST NAME}

Overriding Test Setup from Command Line
    [Setup]  ${CONFIG}
    [Timeout]  NONE
    ${TEST NAME}

Overriding Test Teardown
    [Teardown]  NONE
    [Timeout]  NONE
    ${TEST NAME}

Overriding Test Teardown from Command Line
    [Teardown]  ${CONFIG}
    [Timeout]  NONE
    ${TEST NAME}

Overriding Test Template
    [Timeout]  NONE
    [Template]  NONE
    No Operation

Overriding Test Timeout
    [Timeout]  NONE
    [Template]  NONE
    Sleep  123ms

Overriding Test Timeout from Command Line
    [Timeout]  ${CONFIG}
    [Template]  NONE
    Sleep  123ms

Overriding Default Tags
    [Tags]  NONE
    [Timeout]  NONE
    ${TEST NAME}

Overriding Default Tags from Command Line
    [Tags]  ${CONFIG}
    [Timeout]  NONE
    ${TEST NAME}

Overriding Is Case Insensitive
    [Setup]     none
    [Teardown]  NoNe
    [Template]  nonE
    [Tags]      NONe
    [Timeout]   noNE
    No Operation
