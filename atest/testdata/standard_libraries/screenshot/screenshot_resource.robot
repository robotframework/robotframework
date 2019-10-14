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
    @{actual_png_files}=  List Directory  ${directory}  *.png  absolute
    @{actual_jpeg_files}=  List Directory  ${directory}  *.jp*g  absolute
    @{all_files}=  Combine Lists  ${actual_png_files}  ${actual_jpeg_files}
    List Should Contain Sub List  ${files}  ${all_files}
