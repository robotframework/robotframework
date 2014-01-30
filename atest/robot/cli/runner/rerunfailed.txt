*** Settings ***
Suite Setup       Suite initialization
Suite Teardown    Remove Directory    ${RERUN DIR}    recursive
Force Tags        regression    pybot    jybot
Resource          atest_resource.txt

*** Variables ***
${ORIG DIR}           ${DATADIR}/cli/runfailed
${RERUN DIR}          %{TEMPDIR}/rerun-dir
${SUITE DIR}          ${RERUN DIR}/suite
${RUN FAILED FROM}    ${RERUN DIR}/rerun-output.xml

*** Test Cases ***
Passing is not re-executed
    Run Keyword And Expect Error    No test 'Passing' found*    Check Test Case    Passing

Failing is re-executed
    Check Test Case    Failing

Failing from subsuite is executed
    Check Test Case    Really Failing

Explicitly selected is executed
    Check Test Case    Selected

Excluded failing is not executed
    Run Keyword And Expect Error    No test 'Failing with tag' found*    Check Test Case    Failing with tag

Non-existing failing from output file is not executed
    Run Keyword And Expect Error    No test 'Only in one suite' found*    Check Test Case    Only in one suite

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
    Copy File    ${ORIG DIR}/runfailed1.txt    ${SUITE DIR}/runfailed.txt
    Run Tests    ${EMPTY}    ${SUITE DIR}
    Copy File    ${OUTFILE}    ${RUN FAILED FROM}
    Copy File    ${ORIG DIR}/runfailed2.txt    ${SUITE DIR}/runfailed.txt
    Run Tests    --rerunfailed ${RUN FAILED FROM} --test Selected --exclude tag    ${SUITE DIR}
