*** Settings ***
Non Existing      Setting
Suite Setup       No Operation
Suite Teardown    No Operation
Test Setup        No Operation
Test Teardown     No Operation

*** TestCases ***
Few Pass Markers
    No Operation
    No Operation
    No Operation

Few Pass And Fail Markers
    No Operation
    Run keyword and continue on failure    Fail
    No Operation
    Run keyword and continue on failure    Fail
    No Operation

More Markers Than Fit Into Status Area
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation

Warnings Are Shown Correctly
    No Operation
    No Operation
    No Operation
    Log    Warning    WARN
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    No Operation
    Log    Second warning    WARN
    No Operation
    No Operation
