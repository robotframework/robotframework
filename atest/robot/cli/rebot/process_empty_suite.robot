*** Settings ***
Suite Setup       Create empty input file
Suite Teardown    Remove file    ${EMPTY INPUT}
Resource          rebot_cli_resource.robot

*** Variables ***
${EMPTY INPUT}    %{TEMPDIR}/empty-input.xml

*** Test Cases ***
No tests in file
    Rebot empty suite    --processemptysuite    ${EMPTY INPUT}

Empty suite after filtering by tags
    Rebot empty suite    --ProcessEmptySuite --include nonex    ${INPUT FILE}

Empty suite after filtering by names
    Rebot empty suite    --ProcessEmpty --test nonex    ${INPUT FILE}

Empty multi source suite after filtering
    Rebot empty suite    --ProcessE --test nonex    ${INPUT FILE} ${INPUT FILE}

Empty input is fine with other inputs by default
    Run rebot    ${EMPTY}    ${EMPTY INPUT} ${INPUT FILE}
    Should be empty    ${SUITE.suites[0].tests}
    Should not be empty    ${SUITE.suites[1].tests}
    Stderr should be empty

*** Keywords ***
Create empty input file
    Run Tests Without Processing Output    --include nonex --RunEmptySuite    ${TEST FILE}
    Move File    ${OUTFILE}    ${EMPTY INPUT}

Rebot empty suite
    [Arguments]    ${options}    ${sources}
    Run rebot    ${options} -l log.html -r report.html    ${sources}
    Should be empty    ${SUITE.tests}
    Should be empty    ${SUITE.suites}
    Stderr should be empty
