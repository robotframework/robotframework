*** Settings ***
LIbrary    OperatingSystem
Resource   resources.html
Variables  variables.py

*** Test case ***
Library Import
    Fail If File Exists  ${CURDIR}${/}non_existing.file
    
Resource Import
    Should be Equal  ${resource_file_var}  Variable from a resource file
    
Variable Import
    Should be Equal  ${variable_file_var}  Variable from a variable file
