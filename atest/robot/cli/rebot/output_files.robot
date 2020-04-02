*** Settings ***
Test Template     Correct outputs should be created
Resource          rebot_cli_resource.robot

*** Test Cases ***
Default outputs
    ${EMPTY}    log.html    report.html

Output Only
    --output myoutput.xml --log none --report none    myoutput.xml

Report Only
    --output none --report myreport.html --log NONE    myreport.html

Log Only
    --output None --report NONE --log mylog.html    mylog.html

All Outputs
    -o myoutput.xml -r myreport.html -l mylog.html    mylog.html    myoutput.xml    myreport.html

Outputs Without Extensions
    --output xoutput --report xreport --log xlog    xlog.html    xoutput.xml    xreport.html

Outputs Into Different Directories
    [Template]    NONE
    ${options} =    Catenate
    ...    --outputdir ::invalid::
    ...    --output ${OUTDIR}/out/o/o
    ...    --report ${OUTDIR}/out/r/r
    ...    --log ${OUTDIR}/out/l/l.html
    ${result} =    Run Rebot    ${options}    ${INPUT FILE}    output=${OUTDIR}/out/o/o.xml
    Should Be Equal    ${result.rc}    ${0}
    Directory Should Contain    ${OUTDIR}/out/o    o.xml
    Directory Should Contain    ${OUTDIR}/out/r    r.html
    Directory Should Contain    ${OUTDIR}/out/l    l.html
    Directory Should Contain    ${OUTDIR}/out/    l    o    r

Non-writable Output File
    [Template]    NONE
    Create Directory    %{TEMPDIR}/diréctöry.xml
    ${options} =    Catenate
    ...    -d ${OUTDIR}/out
    ...    -o %{TEMPDIR}/diréctöry.xml
    ...    -r r.html
    ...    -l l
    ${result} =    Run Rebot    ${options}    ${INPUT FILE}    output=NONE
    Should Be Equal    ${result.rc}    ${0}
    Directory Should Contain    ${OUTDIR}/out    l.html    r.html
    Should Match Regexp    ${result.stdout}    ^Log: .*\nReport: .*$
    Should Match Regexp    ${result.stderr}    (?s)^\\[ ERROR \\] Opening output file '.*diréctöry.xml' failed: .*$

*** Keywords ***
Correct outputs should be created
    [Arguments]    ${arguments}    @{expected}
    ${outputs} =    Run rebot and return outputs    ${arguments}
    Lists Should Be Equal    ${outputs}    ${expected}
