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
    [Arguments]  ${directory}  @{files}    ${format}=jpg
    ${file_ext_re} =    Set Variable If    "${format.lower()}" == "jpg"    *.jp*g    *.${format}
    @{actual files}=  List Directory  ${directory}  ${file_ext_re}
    Lists Should Be Equal  ${actual files}  ${files}
