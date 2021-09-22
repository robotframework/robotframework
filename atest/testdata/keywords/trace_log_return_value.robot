*** Settings ***
Library           TraceLogArgsLibrary.py

*** Test Cases ***
Return from user keyword
    Return Value From UK

Return from library keyword
    Set Variable    value

Return from Run Keyword
    Run Keyword    Set Variable    value

Return non-string value
    Convert To Integer    1

Return None
    No Operation

Return non-ASCII string
    Set Variable    Hyvää 'Päivää'\n

Return object with non-ASCII repr
    Return object with non ASCII repr

Return object with invalid repr
    Return object with invalid repr

*** Keywords ***
Return Value From UK
    ${return} =    Set Variable    value
    [Return]    ${return}
