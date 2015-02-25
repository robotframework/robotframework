*** Settings ***
Suite Setup       Suite initialization
Suite Teardown    Remove Directory    ${RERUN DIR}    recursive
Force Tags        regression    pybot    jybot
Resource          atest_resource.robot

*** Variables ***
${ORIG DIR}           ${DATADIR}/cli/runfailed
${RERUN DIR}          %{TEMPDIR}/rerun-dir
${SUITE DIR}          ${RERUN DIR}/suite
${RUN FAILED FROM}    ${RERUN DIR}/rerun-output.xml

*** Test Cases ***
Passing is not re-executed
    Test Should Not Have Been Executed    Passing

Failing is re-executed
    Test Should Have Been Executed    Failing

Failing from subsuite is executed
    Test Should Have Been Executed    Really Failing

Explicitly selected is executed
    Test Should Have Been Executed    Selected

Excluded failing is not executed
    Test Should Not Have Been Executed    Failing with tag

Non-existing failing from output file is not executed
    Test Should Not Have Been Executed    Only in one suite

Suite teardown failures are noticed
    Test Should Have Been Executed    Test passed but suite teardown fails

--runfailed still works without warnings
    [Documentation]    --runfailed should be deprecated in RF 2.9 and removed later
    Run Tests    --runfailed ${RUN FAILED FROM} --test Selected --exclude tag    ${SUITE DIR}
    Should Be Empty    ${ERRORS}
    Run Keyword And Expect Error    No test 'Passing' found*    Check Test Case    Passing
    Check Test Case    Failing
    Check Test Case    Really Failing
    Check Test Case    Selected
    Run Keyword And Expect Error    No test 'Failing with tag' found*    Check Test Case    Failing with tag
    Run Keyword And Expect Error    No test 'Only in one suite' found*    Check Test Case    Only in one suite

*** Keywords ***
Suite initialization
    Copy Directory    ${ORIG DIR}/suite    ${SUITE DIR}
    Copy File    ${ORIG DIR}/runfailed1.robot    ${SUITE DIR}/runfailed.txt
    Run Tests    ${EMPTY}    ${SUITE DIR}
    Copy File    ${OUTFILE}    ${RUN FAILED FROM}
    Copy File    ${ORIG DIR}/runfailed2.robot    ${SUITE DIR}/runfailed.txt
    Run Tests    --rerunfailed ${RUN FAILED FROM} --test Selected --exclude tag    ${SUITE DIR}

Test Should Have Been Executed
    [Arguments]    ${name}
    Check Test Case    ${name}

Test Should Not Have Been Executed
    [Arguments]    ${name}
    Run Keyword And Expect Error    No test '${name}' found*    Check Test Case    ${name}
