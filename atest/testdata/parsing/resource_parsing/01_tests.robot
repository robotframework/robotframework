*** Settings ***
Resource          02_resource.robot

*** Test Cases ***
Test 1.1
    Keyword From 02 Resource
    Log    ${var_from_02_resource}
