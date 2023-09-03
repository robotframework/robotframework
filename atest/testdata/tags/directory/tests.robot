*** Settings ***
Test Tags       test file    tags

*** Test Cases ***
No own tags
    No Operation

Own tags
    [Tags]    own    tags
    No Operation
