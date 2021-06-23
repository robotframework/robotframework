*** Settings ***
Test Teardown     Remove Files    ${MERGE}
Suite Teardown    Remove Files    ${ORIGINAL}
Resource          rebot_resource.robot

*** Variables ***
${MERGE HEADER}   Test has been re-executed and results merged.

*** Variables ***
${DATA}                   ${DATADIR}/rebot/merge_html.robot
${ORIGINAL}               %{TEMPDIR}/merge-original.xml
${MERGE}                  %{TEMPDIR}/merge.xml
@{ALL TESTS}              Html1   Html2   Html3   Html4
${RUN_MSG_TEXT}           Test message
${RUN_MSG_HTML}           *HTML* <b>Test</b> message
${MERGE_MSG_TEXT_TEXT}    SEPARATOR=
...    *HTML* <span class="merge">${MERGE HEADER}</span>
...    <hr>
...    <span class="new-status">New status:</span> <span class="fail">FAIL</span>
...    <br>
...    <span class="new-message">New message:</span> Test message
...    <br>
...    <hr>
...    <span class="old-status">Old status:</span> <span class="fail">FAIL</span>
...    <br>
...    <span class="old-message">Old message:</span> Test message
...    <br>
${MERGE_MSG_HTML_HTML}    SEPARATOR=
...    *HTML* <span class="merge">${MERGE HEADER}</span>
...    <hr>
...    <span class="new-status">New status:</span> <span class="fail">FAIL</span>
...    <br>
...    <span class="new-message">New message:</span> <b>Test</b> message
...    <br>
...    <hr>
...    <span class="old-status">Old status:</span> <span class="fail">FAIL</span>
...    <br>
...    <span class="old-message">Old message:</span> <b>Test</b> message
...    <br>
${MERGE_MSG_TEXT_HTML}    SEPARATOR=
...    *HTML* <span class="merge">${MERGE HEADER}</span>
...    <hr>
...    <span class="new-status">New status:</span> <span class="fail">FAIL</span>
...    <br>
...    <span class="new-message">New message:</span> Test message
...    <br>
...    <hr>
...    <span class="old-status">Old status:</span> <span class="fail">FAIL</span>
...    <br>
...    <span class="old-message">Old message:</span> <b>Test</b> message
...    <br>
${MERGE_MSG_HTML_TEXT}    SEPARATOR=
...    *HTML* <span class="merge">${MERGE HEADER}</span>
...    <hr>
...    <span class="new-status">New status:</span> <span class="fail">FAIL</span>
...    <br>
...    <span class="new-message">New message:</span> <b>Test</b> message
...    <br>
...    <hr>
...    <span class="old-status">Old status:</span> <span class="fail">FAIL</span>
...    <br>
...    <span class="old-message">Old message:</span> Test message
...    <br>

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
    Create Output With Robot    ${ORIGINAL}    ${EMPTY}    ${DATA}
    Should Contain Tests    ${SUITE}    @{ALL TESTS}

Re-run tests
    [Arguments]    ${options}=
    Create Output With Robot    ${MERGE}    --rerunfailed ${ORIGINAL} ${options}    ${DATA}

Run merge
    [Arguments]    ${options}=
    Run Rebot    --merge ${options}    ${ORIGINAL} ${MERGE}
    Stderr Should Be Empty
