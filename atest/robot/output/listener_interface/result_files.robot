*** Settings ***
Documentation     Testing that listener gets information about different output files.
...               Tests also that the listener can be taken into use with path.
Suite Teardown    Remove Listener Files
Resource          listener_resource.robot

*** Variables ***
${LISTENERS}      ${CURDIR}${/}..${/}..${/}..${/}testresources${/}listeners

*** Test Cases ***
Output files
    ${options} =    Catenate
    ...    --listener "${LISTENERS}${/}ListenAll.py"
    ...    --output myout.xml
    ...    --report myrep.html
    ...    --log mylog.html
    ...    --xunit myxun.xml
    ...    --debugfile mydeb.txt
    Run Tests    ${options}    misc/pass_and_fail.robot    output=${OUTDIR}/myout.xml
    Validate result files
    ...    Debug: mydeb.txt
    ...    Output: myout.xml
    ...    Xunit: myxun.xml
    ...    Log: mylog.html
    ...    Report: myrep.html

Output files disabled
    ${options} =    Catenate
    ...    --listener "${LISTENERS}${/}ListenAll.py:output_file_disabled=True"
    ...    --log NONE
    ...    --report NONE
    ...    --output NONE
    Run Tests Without Processing Output    ${options}    misc/pass_and_fail.robot
    Validate result files
    ...    Output: None

*** Keywords ***
Validate result files
    [Arguments]    @{files}
    ${file} =    Get Listener File    ${ALL_FILE}
    ${expected} =    Catenate    SEPARATOR=\n
    ...    @{files}
    ...    Closing...\n
    Should End With    ${file}    ${expected}
    Stderr Should Be Empty
