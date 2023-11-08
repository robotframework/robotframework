*** Settings ***
Resource           atest_resource.robot

*** Variables ***
${CLI OUTDIR}      %{TEMPDIR}${/}cli
${TEST FILE}       misc${/}normal.robot

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
    ${result} =    Run Tests    -d ${CLI OUTDIR} ${options}   ${TEST FILE}    default options=    output=
    Should Be Equal    ${result.rc}    ${0}
    RETURN    ${result}

Tests Should Pass Without Errors
    [Arguments]    ${options}    ${datasource}
    ${result} =    Run Tests    ${options}    ${datasource}
    Should Be Equal    ${SUITE.status}    PASS
    Should Be Empty    ${result.stderr}
    RETURN    ${result}

Run Should Fail
    [Arguments]    ${options}    ${error}    ${regexp}=False
    ${result} =    Run Tests    ${options}    default options=    output=
    Should Be Equal As Integers    ${result.rc}    252
    Should Be Empty    ${result.stdout}
    IF    ${regexp}
        Should Match Regexp    ${result.stderr}    ^\\[ ERROR \\] ${error}${USAGETIP}$
    ELSE
        Should Be Equal    ${result.stderr}    [ ERROR ] ${error}${USAGETIP}
    END
