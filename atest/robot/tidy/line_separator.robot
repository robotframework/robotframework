*** Settings ***
Resource          tidy_resource.robot
Test Setup        Create Directory     ${TEMP}
Test Teardown     Remove Directory     ${TEMP}    recursive=True
Test Template     Output should be correct and have correct line separators


*** Test Cases ***
Default
    ${EMPTY}                    golden.robot     ${\n}

Native
    --lineseparator native      golden.robot     ${\n}

Windows
    -l WINDOWS                  golden.robot    \r\n

Unix
    --lineseparator unix        golden.robot     \n

*** Keywords ***
Output should be correct and have correct line separators
    [Arguments]    ${options}    ${expected file}    ${expected separator}
    ${output} =    Run tidy with golden file and check result    ${options}    ${expected file}
    File should have correct line separators    ${output}    ${expected separator}
