*** Settings ***
Resource          03_resource.robot
Resource          02_resource.robot

*** Test Cases ***
Test 4.1
    Keyword From 02 Resource
    Log    ${var_from_02_resource}

Test 4.2
    Keyword From 03 Resource
    Log    ${var_from_03_resource}
