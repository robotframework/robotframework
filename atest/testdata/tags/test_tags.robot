*** Settings ***
Test Tags       test    tags

*** Test Cases ***
No own tags
    No Operation

Own tags
    [Tags]    own    tags
    No Operation
