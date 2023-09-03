*** Settings ***
Resource        cli_resource.robot

*** Variables ***
${NO TESTS DIR}     %{TEMPDIR}/robot_test_run_empty_suite
${NO TESTS FILE}    ${NO TESTS DIR}.robot

*** Test Cases ***
No tests in file
     [Setup]    Create file    ${NO TESTS FILE}    *** Test Cases ***
     Run empty suite    --runemptysuite    ${NO TESTS FILE}
     [Teardown]    Remove file    ${NO TESTS FILE}

No tests in directory
     [Setup]    Create directory    ${NO TESTS DIR}
     Run empty suite    --runemptysuite    ${NO TESTS DIR}
     [Teardown]    Remove directory    ${NO TESTS DIR}

Empty suite after filtering by tags
     Run empty suite   --Run-Empty-Suite --include nonex   ${TEST FILE}

Empty suite after filtering by names
     Run empty suite   --RunEmptySuite --test nonex   ${TEST FILE}

Empty multi source suite after filtering
     Run empty suite   --RunEmptySuite --test nonex   ${TEST FILE} ${TEST FILE}

*** Keywords ***
Run empty suite
     [Arguments]    ${options}    ${sources}
     Run tests     ${options} -l log.html -r report.html    ${sources}
     Should be empty    ${SUITE.tests}
     Should be empty    ${SUITE.suites}
     Stderr should be empty
