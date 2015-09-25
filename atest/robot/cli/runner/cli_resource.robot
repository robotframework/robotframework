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
    ${result} =    Run Robot Directly    -d ${CLI OUTDIR} ${options} ${path}
    Should Contain    ${result.stdout}    Output:    message=Running tests failed for some reason
    [Return]    ${result.stdout}

Tests Should Pass Without Errors
    [Arguments]    ${options}    ${datasource}
    Run Tests    ${options}    ${datasource}
    Should Be Equal    ${SUITE.status}    PASS
    File Should Be Empty    ${STDERR FILE}

Run Should Fail
    [Arguments]    ${options}    ${exp error}
    ${result} =    Run Robot Directly  ${options}
    Should Be Equal As Integers    ${result.rc}    252
    Should Match Regexp    ${result.stdout}    ^\\[ .*ERROR.* \\] ${exp error}${USAGETIP}$
