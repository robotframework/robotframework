*** Settings ***
Resource          02_resource.robot

*** Variables ***
${var_from_03_resource}    variable value from 03 resource

*** Keywords ***
Keyword From 03 Resource
    Log    ${var_from_03_resource}
    Log    ${var_from_02_resource}
    Keyword From 02 Resource
