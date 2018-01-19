*** Settings ***
Test Teardown     Remove Files    ${MERGE 1}
Suite Teardown    Remove Files    ${ORIGINAL}
Resource          rebot_resource.robot

*** Variables ***
${MISC}             ${DATADIR}/rebot/
${SUITES}           ${DATADIR}/rebot/suites
${ORIGINAL}         %{TEMPDIR}/merge-original.xml
${MERGE 1}          %{TEMPDIR}/merge-1.xml
@{ALL TESTS}        Html1   Html2   Html3   Html4
@{ALL SUITES}       Htmlsuite
${RUN_MSG_TEXT}     Test message
${RUN_MSG_HTML}     *HTML*<b>Test</b> message
${MERGE_MSG_TEXT_TEXT}   *HTML*Re-executed test has been merged.<hr>New status:\ \ <span class="fail">FAIL</span><br>New message:\ \ Test message<hr>Old status:\ \ <span class="fail">FAIL</span><br>Old message:\ \ Test message
${MERGE_MSG_HTML_HTML}   *HTML*Re-executed test has been merged.<hr>New status:\ \ <span class="fail">FAIL</span><br>New message:\ \ <b>Test</b> message<hr>Old status:\ \ <span class="fail">FAIL</span><br>Old message:\ \ <b>Test</b> message
${MERGE_MSG_TEXT_HTML}   *HTML*Re-executed test has been merged.<hr>New status:\ \ <span class="fail">FAIL</span><br>New message:\ \ Test message<hr>Old status:\ \ <span class="fail">FAIL</span><br>Old message:\ \ <b>Test</b>  message
${MERGE_MSG_HTML_TEXT}   *HTML*Re-executed test has been merged.<hr>New status:\ \ <span class="fail">FAIL</span><br>New message:\ \ <b>Test</b> message<hr>Old status:\ \ <span class="fail">FAIL</span><br>Old message:\ \ Test message

*** Test Cases ***
Merge re-executed tests
    Run original tests
    Re-run tests    options=--variable USE_HTML:True
    Should Contain Tests    ${SUITE}
    ...     Html1=FAIL:${RUN_MSG_TEXT}
    ...     Html2=FAIL:${RUN_MSG_HTML}
    ...     Html3=FAIL:${RUN_MSG_HTML}
    ...     Html4=FAIL:${RUN_MSG_TEXT}
    Run merge
    Should Contain Tests    ${SUITE}
    ...     Html1=FAIL:${MERGE_MSG_TEXT_TEXT}
    ...     Html2=FAIL:${MERGE_MSG_HTML_TEXT}
    ...     Html3=FAIL:${MERGE_MSG_HTML_HTML}
    ...     Html4=FAIL:${MERGE_MSG_TEXT_HTML}

*** Keywords ***
Run original tests
    Create Output With Robot    ${ORIGINAL}    ${EMPTY}    ${SUITES}
    Verify original tests

Verify original tests
    Should Be Equal    ${SUITE.name}    Suites
    Should Contain Tests    ${SUITE}    @{ALL TESTS}

Re-run tests
    [Arguments]    ${options}=
    Create Output With Robot    ${MERGE 1}    --rerunfailed ${ORIGINAL} ${options}    ${SUITES}

Run merge
    [Arguments]    ${options}=
    Run Rebot    --merge ${options}    ${ORIGINAL} ${MERGE 1}
    Stderr Should Be Empty
