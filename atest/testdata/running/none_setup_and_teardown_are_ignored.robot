*** Settings ***
Documentation    NO RIDE because it would clean-up formatting.
Suite Setup      NONE
Suite Teardown   none
Test Setup       NoNe
Test Teardown    NOne

*** Test Cases ***
None default setup and teardown
    No Operation

None custom setup and teardown
    [Setup]    NONE
    No Operation
    [Teardown]    none
