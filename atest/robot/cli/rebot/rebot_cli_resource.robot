*** Settings ***
Resource          ../runner/cli_resource.robot

*** Variables ***
${TEST FILE}      misc/normal.robot
${INPUT FILE}     %{TEMPDIR}${/}rebot-cli-input.xml
${M_211_211}      2 critical tests, 1 passed, 1 failed\n2 tests total, 1 passed, 1 failed
${M_110_211}      1 critical test, 1 passed, 0 failed\n2 tests total, 1 passed, 1 failed
${M_101_211}      1 critical test, 0 passed, 1 failed\n2 tests total, 1 passed, 1 failed
${M_000_211}      0 critical tests, 0 passed, 0 failed\n2 tests total, 1 passed, 1 failed

*** Keywords ***
Run tests to create input file for Rebot
    [Arguments]    ${tests}=${TEST FILE}    ${input}=${INPUT FILE}
    Run Tests Without Processing Output    --loglevel TRACE    ${tests}
    Move File    ${OUTFILE}    ${input}

Run rebot and return outputs
    [Arguments]    ${options}
    Create Output Directory
    ${result} =    Run Rebot    --outputdir ${CLI OUTDIR} ${options}    ${INPUT FILE}    default options=    output=
    Should Be Equal    ${result.rc}    ${0}
    @{outputs} =    List Directory    ${CLI OUTDIR}
    RETURN    @{outputs}
