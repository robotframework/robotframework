*** Settings ***
Resource            atest_resource.robot

*** Variables ***
${INPUT 1}          ${DATADIR}${/}misc${/}normal.robot
${INPUT 2}          ${DATADIR}${/}misc${/}suites
${INPUT 3}          ${DATADIR}${/}testdoc
${OUTFILE}          %{TEMPDIR}/testdoc-output.html
${ARGFILE 1}        %{TEMPDIR}/testdoc_argfile_1.txt
${ARGFILE 2}        %{TEMPDIR}/testdoc_argfile_2.txt

*** Keywords ***
Run TestDoc
    [Arguments]    @{args}    ${rc}=0    ${remove_outfile}=True
    Run Keyword If    ${remove outfile}    Remove File    ${OUTFILE}
    ${result} =    Run Process    @{INTERPRETER.testdoc}    @{args}    ${OUTFILE}    stderr=STDOUT
    Should Be Equal As Integers    ${result.rc}    ${rc}
    ...    Unpexted rc ${result.rc}. Output was:\n${result.stdout}    values=False
    Set Test Variable    ${OUTPUT}    ${result.stdout}

TestDoc Run Should Fail
    [Arguments]    ${error}    @{args}    ${remove_outfile}=True
    Run TestDoc    @{args}    rc=252    remove_outfile=${remove_outfile}
    Should Match    ${OUTPUT}    ${error}${USAGE TIP}

Testdoc Should Contain
    [Arguments]    @{expected}
    ${testdoc}=    Get File    ${OUTFILE}
    FOR     ${exp}    IN    @{expected}
        Should Contain    ${testdoc}   ${exp}
    END

Testdoc Should Not Contain
    [Arguments]    @{expected}
    ${testdoc}=    Get File    ${OUTFILE}
    FOR     ${exp}    IN    @{expected}
        Should Not Contain    ${testdoc}   ${exp}
    END

Outfile Should Have Correct Line Separators
    File should have correct line separators    ${OUTFILE}

Output Should Contain Outfile
    Should Not Contain    ${OUTPUT}    ERROR
    File Should Exist    ${OUTPUT}
    Remove File    ${OUTFILE}
    File Should Not Exist    ${OUTPUT}

Create Argument File
    [Arguments]    ${path}    @{content}
    ${content} =    Catenate    SEPARATOR=\n    @{content}
    Create File    ${path}    ${content}
