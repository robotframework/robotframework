*** Settings ***
Non Existing      Setting
Suite Setup       No Operation
Suite Teardown    No Operation
Test Setup        No Operation
Test Teardown     No Operation

*** Test Cases ***
Few Pass Markers
    No Operation
    No Operation
    No Operation

Few Pass And Fail Markers
    No Operation
    Run keyword and continue on failure    Fail
    No Operation

More Markers Than Fit Into Status Area During Very Deep Keyword
    KeywordLevel1

Warnings Are Shown Correctly
    No Operation
    No Operation
    No Operation
    Log    Warning    WARN
    No Operation

*** Keywords ***

KeywordLevel1
    KeywordLevel2
KeywordLevel2
    KeywordLevel3
KeywordLevel3
    KeywordLevel4
KeywordLevel4
    KeywordLevel5
KeywordLevel5
    KeywordLevel6
KeywordLevel6
    KeywordLevel7
KeywordLevel7
    KeywordLevel8
KeywordLevel8
    KeywordLevel9
KeywordLevel9
    KeywordLevel10
KeywordLevel10
    KeywordLevel11
KeywordLevel11
    KeywordLevel12
KeywordLevel12
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
