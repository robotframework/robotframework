*** Settings ***
Suite Setup       Suite initialization
Suite Teardown    Remove Directory    ${RERUN SUITE DIR}    recursive
Resource          atest_resource.robot

*** Variables ***
${ORIG DIR}           ${DATADIR}/cli/runfailed
${RERUN SUITE DIR}    %{TEMPDIR}/rerunsuites-dir
${SUITE DIR}          ${RERUN SUITE DIR}/suite
${RUN FAILED FROM}    ${RERUN SUITE DIR}/rerun-suites-output.xml

*** Test Cases ***
Passing suite is not re-executed
    Test Should Not Have Been Executed    Passing

Failing suite is re-executed
    Test Should Have Been Executed   Failing
    Test Should Have Been Executed   Not Failing

Suite teardown failures are noticed
    Test Should Have Been Executed   Test passed but suite teardown fails

Excluded failing is not executed
    Test Should Not Have Been Executed    Failing with tag

Non-existing failing from output file is not executed
    Test Should Not Have Been Executed    Only in one suite

*** Keywords ***
Suite initialization
    Copy Directory    ${ORIG DIR}/suite    ${SUITE DIR}
    Copy File    ${ORIG DIR}/runfailed1.robot     ${SUITE DIR}/runfailed.robot
    Run Tests    ${SUITE DIR}
    Copy File    ${OUTFILE}    ${RUN FAILED FROM}
    Copy File    ${ORIG DIR}/runfailed2.robot     ${SUITE DIR}/runfailed.robot
    Run Tests    --rerunfailedsuites ${RUN FAILED FROM} --exclude excluded_tag ${SUITE DIR}

Test Should Have Been Executed
    [Arguments]    ${name}
    Check Test Case    ${name}

Test Should Not Have Been Executed
    [Arguments]    ${name}
    Run Keyword And Expect Error    No test '${name}' found*    Check Test Case    ${name}
