*** Settings ***
Resource    tidy_resource.robot
Test Setup        Create Directory     ${TEMP}
Test Teardown     Remove Directory     ${TEMP}    recursive=True

*** Test Cases ***
Custom maxlinelength for test suite
    [Template]    Run tidy with golden file and check result
    -m 120 -f txt               golden_120_maxlinelength.robot
    -m 120 -f txt --usepipes    golden_pipes_120_maxlinelength.robot

Custom maxlinelength for resource
    [Template]    Run tidy with golden resource file and check result
    -m 120 -f txt               golden_resource_120_maxlinelength.robot
    -m 120 -f txt --usepipes    golden_pipes_resource_120_maxlinelength.robot
