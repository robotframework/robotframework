*** Settings ***
Resource          tidy_resource.robot
Test Setup        Create Directory     ${TEMP}
Test Teardown     Remove Directory     ${TEMP}    recursive=True
Test Template     Output should be correct and have correct line separators


*** Test Cases ***
Default
    ${EMPTY}                    golden.robot     ${\n}
    -f tsv                      golden.tsv     ${\n}
    --format html               golden.html    ${\n}

Native
    --lineseparator native      golden.robot     ${\n}
    --LineSep Native -f tsv     golden.tsv     ${\n}
    -l NATIVE --format html     golden.html    ${\n}

Windows
    --lineseparator windows     golden.robot     \r\n
    --LineSep Windows -f tsv    golden.tsv     \r\n
    -l WINDOWS --format html    golden.html    \r\n

Unix
    --lineseparator unix        golden.robot     \n
    --LineSep Unix -f tsv       golden.tsv     \n
    -l UNIX --format html       golden.html    \n

*** Keywords ***
Output should be correct and have correct line separators
    [Arguments]    ${options}    ${expected file}    ${expected separator}
    ${output} =    Run tidy with golden file and check result    ${options}    ${expected file}
    File should have correct line separators    ${output}    ${expected separator}
