*** Settings ***
Library         Screenshot
Library         OperatingSystem
Library         Collections

*** Keywords ***
Screenshot Should Exist
    [Arguments]  ${path}
    [Documentation]  Checks that screenshot file exists and is newer than
    ...  timestamp set in test setup.
    File Should Exist  ${path}
    ${filetime} =  Get Modified Time  ${path}
    Should Be True  '${filetime}' >= '${START TIME}'

Save Start Time
    ${start time} =  Get Time
    Set Test Variable  \${START TIME}

Screenshots Should Exist
    [Arguments]  ${directory}  @{files}
    @{actual files}=  List Directory  ${directory}  *.jp*g
    Lists Should Be Equal  ${actual files}  ${files}
