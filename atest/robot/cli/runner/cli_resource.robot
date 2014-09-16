*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${CLI OUTDIR}     %{TEMPDIR}${/}cli
${TEST FILE}      misc${/}normal.robot
${UNICODE TEST}    misc${/}unicode.robot

*** Keywords ***
Create Output Directory
    Remove Directory    ${CLI OUTDIR}    recursive
    Create Directory    ${CLI OUTDIR}

Directory Should Contain
    [Arguments]    ${path}    @{expected}
    ${actual} =    List Directory    ${path}
    Should Be Equal    ${actual}    ${expected}

Output Directory Should Contain
    [Arguments]    @{expected}
    Directory Should Contain    ${CLI OUTDIR}    @{expected}

Output Directory Should Be Empty
    Directory Should Be Empty    ${CLI OUTDIR}

Run Some Tests
    [Arguments]    ${options}=-l none -r none
    ${path} =    Join Path    ${CURDIR}/../../..    testdata    ${TESTFILE}
    ${output} =    Run Robot Directly    -d ${CLI OUTDIR} ${options} ${path}
    Should Contain    ${output}    Output:    message=Running tests failed for some reason
    [Return]    ${output}

Tests Should Pass Without Errors
    [Arguments]    ${options}    ${datasource}
    Run Tests    ${options}    ${datasource}
    Should Be Equal    ${SUITE.status}    PASS
    File Should Be Empty    ${STDERR FILE}

Run Should Fail
    [Arguments]    ${options}    ${exp error}
    Set Runners
    ${rc}    ${output} =    Run And Return RC and Output    ${ROBOT} ${options}
    Should Be Equal As Integers    ${rc}    252
    Should Match Regexp    ${output}    ^\\[ .*ERROR.* \\] ${exp error}${USAGETIP}$
