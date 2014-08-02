*** Settings ***
Library    OperatingSystem
Resource   resources.robot
Variables  variables.py

*** Test Case ***
Library Import
    File Should Not Exist  ${CURDIR}${/}non_existing.file

Resource Import
    Should be Equal  ${resource_file_var}  Variable from a resource file

Variable Import
    Should be Equal  ${variable_file_var}  Variable from a variable file
