*** Settings ***
Suite Setup       Suite initialization
Suite Teardown    Remove Directory    ${RERUN DIR}    recursive
Resource          atest_resource.robot

*** Variables ***
${ORIG DIR}           ${DATADIR}/cli/runfailed
${RERUN DIR}          %{TEMPDIR}/rerun-dir
${SUITE DIR}          ${RERUN DIR}/suite
${RUN FAILED FROM}    ${RERUN DIR}/rerun-output.xml

*** Test Cases ***
Passing is not re-executed
    Test Should Not Have Been Executed    Passing
    Test Should Not Have Been Executed    Not Failing

Skipping test in not re-executed
    Test Should Not Have Been Executed    Skipped

Failing is re-executed
    Test Should Have Been Executed        Failing

Failing from subsuite is executed
    Test Should Have Been Executed        Really Failing

Glob meta characters are ignored in names
    Test Should Have Been Executed        Glob [seq]
    Test Should Have Been Executed        Glob question?
    Test Should Have Been Executed        Glob asterisk*
    Test Should Not Have Been Executed    Glob question!
    Test Should Not Have Been Executed    Glob asteriskXXX

Explicitly selected is executed
    Test Should Have Been Executed        Selected

Excluded failing is not executed
    Test Should Not Have Been Executed    Failing with tag

Non-existing failing from output file is not executed
    Test Should Not Have Been Executed    Only in one suite

Suite teardown failures are noticed
    Test Should Have Been Executed        Test passed but suite teardown fails

*** Keywords ***
Suite initialization
    Copy Directory    ${ORIG DIR}/suite    ${SUITE DIR}
    Copy File    ${ORIG DIR}/runfailed1.robot    ${SUITE DIR}/runfailed.robot
    Run Tests    ${EMPTY}    ${SUITE DIR}
    Copy File    ${OUTFILE}    ${RUN FAILED FROM}
    Copy File    ${ORIG DIR}/runfailed2.robot    ${SUITE DIR}/runfailed.robot
    Run Tests    --rerunfailed ${RUN FAILED FROM} --test Selected --include common --exclude excluded_tag    ${SUITE DIR}

Test Should Have Been Executed
    [Arguments]    ${name}
    Check Test Case    ${name}

Test Should Not Have Been Executed
    [Arguments]    ${name}
    Run Keyword And Expect Error    No test '${name}' found*    Check Test Case    ${name}
