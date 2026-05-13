*** Settings ***
Suite Teardown    Remove Listener Files
Resource          listener_resource.robot

*** Variables ***
${PATH}           %{TEMPDIR}/listen_result_files.txt
${V2}             ${LISTENERS}/ListenAll.py
${V3}             ${DATADIR}/output/listener_interface/ResultFiles.py

*** Test Cases ***
Result files with v2 listener
    VAR    ${options}
    ...    --listener "${V2}${:}${PATH}"
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

Result files disables with v2 listener
    VAR    ${options}
    ...    --listener "${V2}${:}${PATH}${:}output_file_disabled=True"
    ...    --log NONE
    ...    --report NONE
    ...    --output NONE
    Run Tests Without Processing Output    ${options}    misc/pass_and_fail.robot
    Validate result files
    ...    Output: None

Result files with v3 listener
    VAR    ${options}
    ...    --listener "${V3}${:}${PATH}"
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

Result files disables with v3 listener
    VAR    ${options}
    ...    --listener "${V3}${:}${PATH}${:}output_file_disabled=True"
    ...    --log NONE
    ...    --report NONE
    ...    --output NONE
    Run Tests Without Processing Output    ${options}    misc/pass_and_fail.robot
    Validate result files
    ...    Output: None

Only 'result_file' method with v3 listener
    VAR    ${options}
    ...    --listener "${V3}${:}${PATH}${:}only_result_file=True"
    ...    --output myout.xml
    ...    --report myrep.html
    ...    --log mylog.html
    ...    --xunit myxun.xml
    ...    --debugfile mydeb.txt
    Run Tests    ${options}    misc/pass_and_fail.robot    output=${OUTDIR}/myout.xml
    Validate result files
    ...    DEBUG: mydeb.txt
    ...    OUTPUT: myout.xml
    ...    XUNIT: myxun.xml
    ...    LOG: mylog.html
    ...    REPORT: myrep.html

Result files disables with v3 listener having only 'result_file' method
    VAR    ${options}
    ...    --listener "${V3}${:}${PATH}${:}output_file_disabled=True:only_result_file=True"
    ...    --log NONE
    ...    --report NONE
    ...    --output NONE
    Run Tests Without Processing Output    ${options}    misc/pass_and_fail.robot
    Validate result files

*** Keywords ***
Validate result files
    [Arguments]    @{files}
    VAR    ${expected}
    ...    @{files}
    ...    Closing...\n
    ...    separator=\n
    ${file} =    Get File    ${PATH}
    Should End With    ${file}    ${expected}
    Stderr Should Be Empty
