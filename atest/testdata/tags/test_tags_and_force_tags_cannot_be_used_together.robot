*** Settings ***
Test Tags     test    tags
Force Tags    ignored

*** Test Cases ***
No own tags
    No Operation

Own tags
    [Tags]    own    tags
    No Operation
