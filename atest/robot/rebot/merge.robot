*** Settings ***
Suite Setup       Run original tests
Test Teardown     Remove Files    ${MERGE 1}    ${MERGE 2}
Suite Teardown    Remove Files    ${ORIGINAL}
Resource          rebot_resource.robot

*** Variables ***
${MISC}           ${DATADIR}/misc/
${SUITES}         ${DATADIR}/misc/suites
${ORIGINAL}       %{TEMPDIR}/merge-original.xml
${MERGE 1}        %{TEMPDIR}/merge-1.xml
${MERGE 2}        %{TEMPDIR}/merge-2.xml
@{ALL TESTS}      Suite4 First             SubSuite1 First    SubSuite2 First
...               Test From Sub Suite 4    SubSuite3 First    SubSuite3 Second
...               Suite1 First             Suite1 Second
...               Test With Double Underscore    Test With Prefix    Third In Suite1
...               Suite2 First             Suite3 First
@{ALL SUITES}     Fourth                   Subsuites          Custom name for 📂 'subsuites2'
...               Suite With Double Underscore    Suite With Prefix
...               Tsuite1                  Tsuite2            Tsuite3
@{SUB SUITES 1}   Sub1                     Sub2
@{SUB SUITES 2}   Sub.suite.4              Custom name for 📜 'subsuite3.robot'
@{RERUN TESTS}    Suite4 First             SubSuite1 First
@{RERUN SUITES}   Fourth                   Subsuites

*** Test Cases ***
Merge re-executed tests
    Re-run tests
    Run merge
    Test merge should have been successful

Merge suite setup and teardown
    [Setup]   Should Be Equal    ${PREV_TEST_STATUS}    PASS
    Suite setup and teardown should have been merged

Merge suite documentation and metadata
    [Setup]   Should Be Equal    ${PREV_TEST_STATUS}    PASS
    Suite documentation and metadata should have been merged

Merge re-executed and re-re-executed tests
    Re-run tests
    Re-re-run tests
    Run multi-merge
    ${message} =    Create expected multi-merge message
    Test merge should have been successful    status 2=FAIL    message 2=${message}

Add new tests
    Run tests to be added
    Run merge
    Test add should have been successful

Add nested suite
    Run suite to be added
    Run merge
    Suite add should have been successful

Merge warnings
    Re-run tests    --variable LEVEL:WARN --variable MESSAGE:Override
    Run merge
    Test merge should have been successful
    Warnings should have been merged

Non-matching root suite
    Run incompatible suite
    Run incompatible merge
    Merge should have failed

Using other options
    [Documentation]  Test that other command line options works normally with
    ...              --merge. Most importantly verify that options handled
    ...              by ExecutionResult (--flattenkeyword) work correctly.
    Re-run tests
    Run merge    --nomerge --log log.html --merge --flattenkeyword name:BuiltIn.Fail --name Custom
    Test merge should have been successful    suite name=Custom
    Log should have been created with Fail keywords flattened

Merge ignores skip
    Create Output With Robot    ${ORIGINAL}    ${EMPTY}    rebot/merge_statuses.robot
    Create Output With Robot    ${MERGE1}    --skip NOTskip    rebot/merge_statuses.robot
    Run Merge
    ${prefix} =    Catenate
    ...    *HTML* Test has been re-executed and results merged.
    ...    Latter result had <span class="skip">SKIP</span> status and was ignored. Message:
    Should Contain Tests    ${SUITE}
    ...    Pass=PASS:${prefix}\nTest skipped using '--skip' command line option.
    ...    Fail=FAIL:${prefix}\nTest skipped using '--skip' command line option.<hr>Original message:\nNot &lt;b&gt;HTML&lt;/b&gt; fail
    ...    Skip=SKIP:${prefix}\n<b>HTML</b> skip<hr>Original message:\n<b>HTML</b> skip

*** Keywords ***
Run original tests
    ${options} =    Catenate
    ...    --variable FAIL:YES
    ...    --variable LEVEL:WARN
    ...    --doc "Doc for original run"
    ...    --metadata Original:True
    Create Output With Robot    ${ORIGINAL}    ${options}    ${SUITES}
    Verify original tests

Verify original tests
    Should Be Equal    ${SUITE.name}    Suites
    Should Contain Suites    ${SUITE}    @{ALL SUITES}
    Should Contain Suites    ${SUITE.suites[2]}    @{SUB SUITES 1}
    Should Contain Suites    ${SUITE.suites[3]}    @{SUB SUITES 2}
    Should Contain Tests    ${SUITE}    @{ALL TESTS}
    ...    SubSuite1 First=FAIL:This test was doomed to fail: YES != NO

Re-run tests
    [Arguments]    ${options}=
    ${options} =    Catenate
    ...    --doc "Doc for re-run"
    ...    --metadata ReRun:True
    ...    --variable SUITE_SETUP:NoOperation  # Affects misc/suites/__init__.robot
    ...    --variable SUITE_TEARDOWN:NONE      #           -- ;; --
    ...    --variable SETUP_MSG:Rerun!         # Affects misc/suites/fourth.robot
    ...    --variable TEARDOWN_MSG:New!        #           -- ;; --
    ...    --variable SETUP:NONE               # Affects misc/suites/subsuites/sub1.robot
    ...    --variable TEARDOWN:NONE            #           -- ;; --
    ...    --rerunfailed ${ORIGINAL} ${options}
    Create Output With Robot    ${MERGE 1}    ${options}    ${SUITES}
    Should Be Equal    ${SUITE.name}    Suites
    Should Contain Suites    ${SUITE}    @{RERUN SUITES}
    Should Contain Suites    ${SUITE.suites[1]}    ${SUB SUITES 1}[0]
    Should Contain Tests    ${SUITE}    @{RERUN TESTS}

Re-re-run tests
    Create Output With Robot    ${MERGE 2}    --test SubSuite1First --variable FAIL:again    ${SUITES}

Run tests to be added
    Create Output With Robot    ${MERGE 1}    --name Suites    ${MISC}/pass_and_fail.robot

Run suite to be added
    Create Output With Robot    ${MERGE 1}    --name Suites --suite PassAndFail    ${MISC}

Run incompatible suite
    Create Output With Robot    ${MERGE 1}    ${EMPTY}    ${MISC}/pass_and_fail.robot

Run merge
    [Arguments]    ${options}=
    Run Rebot    --merge ${options}    ${ORIGINAL} ${MERGE 1}
    Stderr Should Be Empty

Run multi-merge
    Run Rebot    -R    ${ORIGINAL} ${MERGE 1} ${MERGE 2}
    Stderr Should Be Empty

Run incompatible merge
    Run Rebot Without Processing Output    --merge    ${ORIGINAL} ${MERGE 1}

Test merge should have been successful
    [Arguments]    ${suite name}=Suites    ${status 1}=FAIL    ${message 1}=
    ...    ${status 2}=PASS    ${message 2}=
    Should Be Equal    ${SUITE.name}    ${suite name}
    Should Contain Suites    ${SUITE}    @{ALL SUITES}
    Should Contain Suites    ${SUITE.suites[2]}    @{SUB SUITES 1}
    Should Contain Suites    ${SUITE.suites[3]}    @{SUB SUITES 2}
    ${message 1} =    Create expected merge message    ${message 1}
    ...    FAIL    Expected    FAIL    Expected
    ${message 2} =    Create expected merge message    ${message 2}
    ...    PASS    ${EMPTY}    FAIL    This test was doomed to fail: YES != NO
    Should Contain Tests    ${SUITE}    @{ALL TESTS}
    ...    Suite4 First=${status 1}:${message 1}
    ...    SubSuite1 First=${status 2}:${message 2}
    Timestamps should be cleared
    ...    ${SUITE}
    ...    ${SUITE.suites[1]}
    ...    ${SUITE.suites[2]}
    ...    ${SUITE.suites[2].suites[0]}
    Timestamps should be set
    ...    ${SUITE.suites[2].suites[1]}
    ...    ${SUITE.suites[3]}
    ...    ${SUITE.suites[3].suites[0]}
    ...    ${SUITE.suites[3].suites[1]}
    ...    ${SUITE.suites[4]}
    ...    ${SUITE.suites[6]}
    ...    ${SUITE.suites[7]}

Suite setup and teardown should have been merged
    Should Be Equal      ${SUITE.setup.full_name}                      BuiltIn.No Operation
    Should Be Equal      ${SUITE.teardown.name}                        ${NONE}
    Should Be Equal      ${SUITE.suites[1].name}                       Fourth
    Check Log Message    ${SUITE.suites[1].setup.msgs[0]}              Rerun!
    Check Log Message    ${SUITE.suites[1].teardown.msgs[0]}           New!
    Should Be Equal      ${SUITE.suites[2].suites[0].name}             Sub1
    Should Be Equal      ${SUITE.suites[2].suites[0].setup.name}       ${NONE}
    Should Be Equal      ${SUITE.suites[2].suites[0].teardown.name}    ${NONE}

Suite documentation and metadata should have been merged
    Should Be Equal      ${SUITE.doc}                                  Doc for re-run
    Should Be Equal      ${SUITE.metadata}[ReRun]                      True
    Should Be Equal      ${SUITE.metadata}[Original]                   True

Test add should have been successful
    Should Be Equal    ${SUITE.name}    Suites
    Should Contain Suites    ${SUITE}    @{ALL SUITES}
    Should Contain Suites    ${SUITE.suites[2]}    @{SUB SUITES 1}
    Should Contain Suites    ${SUITE.suites[3]}    @{SUB SUITES 2}
    Should Contain Tests    ${SUITE}    @{ALL TESTS}
    ...    SubSuite1 First=FAIL:This test was doomed to fail: YES != NO
    ...    Pass=PASS:*HTML* Test added from merged output.
    ...    Fail=FAIL:*HTML* Test added from merged output.<hr>Expected failure
    Timestamps should be cleared
    ...    ${SUITE}
    Timestamps should be set
    ...    ${SUITE.suites[1]}
    ...    ${SUITE.suites[2]}
    ...    ${SUITE.suites[2].suites[0]}
    ...    ${SUITE.suites[2].suites[1]}
    ...    ${SUITE.suites[3]}
    ...    ${SUITE.suites[3].suites[0]}
    ...    ${SUITE.suites[3].suites[1]}
    ...    ${SUITE.suites[4]}
    ...    ${SUITE.suites[6]}
    ...    ${SUITE.suites[7]}

Suite add should have been successful
    Should Be Equal    ${SUITE.name}    Suites
    Should Contain Suites    ${SUITE}    @{ALL SUITES}    Pass And Fail
    Should Contain Suites    ${SUITE.suites[2]}    @{SUB SUITES 1}
    Should Contain Suites    ${SUITE.suites[3]}    @{SUB SUITES 2}
    Should Contain Tests    ${SUITE}    @{ALL TESTS}
    ...    Pass    Fail
    ...    SubSuite1 First=FAIL:This test was doomed to fail: YES != NO
    Should Be Equal    ${SUITE.suites[8].name}    Pass And Fail
    Should Contain Tests    ${SUITE.suites[8]}    Pass    Fail
    Should Be Equal    ${SUITE.suites[8].message}    *HTML* Suite added from merged output.
    Timestamps should be cleared
    ...    ${SUITE}
    Timestamps should be set
    ...    ${SUITE.suites[1]}
    ...    ${SUITE.suites[2]}
    ...    ${SUITE.suites[2].suites[0]}
    ...    ${SUITE.suites[2].suites[1]}
    ...    ${SUITE.suites[3]}
    ...    ${SUITE.suites[3].suites[0]}
    ...    ${SUITE.suites[3].suites[1]}
    ...    ${SUITE.suites[4]}
    ...    ${SUITE.suites[6]}
    ...    ${SUITE.suites[7]}
    ...    ${SUITE.suites[8]}

Warnings should have been merged
    Length Should Be    ${ERRORS}    2
    Check Log Message    ${ERRORS[0]}    Original message    WARN
    Check Log Message    ${ERRORS[1]}    Override    WARN
    ${tc} =    Check Test Case    SubSuite1 First
    Check Log Message    ${tc.kws[0].msgs[0]}    Override    WARN

Merge should have failed
    Stderr Should Be Equal To
    ...    [ ERROR ] Cannot merge outputs containing different root suites.
    ...    Original suite is 'Suites' and merged is 'Pass And Fail'.${USAGE TIP}\n

Timestamps should be cleared
    [Arguments]    @{suites}
    FOR    ${suite}    IN    @{suites}
        Should Be Equal    ${suite.start_time}    ${None}
        Should Be Equal    ${suite.end_time}    ${None}
    END

Timestamps should be set
    [Arguments]    @{suites}
    FOR    ${suite}    IN    @{suites}
        Timestamp Should Be Valid    ${suite.start_time}
        Timestamp Should Be Valid    ${suite.end_time}
    END

Create expected merge message header
    [Arguments]    ${html marker}=*HTML*${SPACE}
    Run Keyword And Return    Catenate    SEPARATOR=
    ...    ${html marker}<span class="merge">Test has been re-executed and results merged.</span><hr>

Create expected merge old message body
    [Arguments]    ${old status}    ${old message}
    ${old status} =    Set Variable If    '${old status}' == 'PASS'
    ...    <span class="pass">PASS</span>    <span class="fail">FAIL</span>
    ${old message} =    Set Variable If    '${old message}' != ''
    ...    ${old message}<br>    ${EMPTY}
    ${old message html achor} =    Set Variable If    '${old message}' != ''
    ...    <span class="old-message">Old message:</span>${SPACE}    ${EMPTY}
    Run Keyword And Return    Catenate    SEPARATOR=
    ...    <span class="old-status">Old status:</span> ${old status}<br>
    ...    ${old message html achor}${old message}

Create expected merge message body
    [Arguments]    ${new status}    ${new message}    ${old status}    ${old message}
    ${new status} =    Set Variable If    '${new status}' == 'PASS'
    ...    <span class="pass">PASS</span>    <span class="fail">FAIL</span>
    ${new message html achor} =    Set Variable If    '${new message}' != ''
    ...    <span class="new-message">New message:</span>${SPACE}    ${EMPTY}
    ${new message} =    Set Variable If    '${new message}' != ''
    ...    ${new message}<br>    ${EMPTY}
    ${old message} =    Create expected merge old message body    ${old status}    ${old message}
    Run Keyword And Return    Catenate    SEPARATOR=
    ...    <span class="new-status">New status:</span> ${new status}<br>
    ...    ${new message html achor}${new message}
    ...    <hr>${old message}

Create expected merge message
    [Arguments]    ${message}    ${new status}    ${new message}    ${old status}    ${old message}   ${html marker}=*HTML*${SPACE}
    Return From Keyword If    """${message}"""    ${message}
    ${merge header} =    Create expected merge message header    html marker=${html marker}
    ${merge body} =    Create expected merge message body    ${new status}    ${new message}    ${old status}    ${old message}
    Run Keyword And Return    Catenate    SEPARATOR=
    ...    ${merge header}
    ...    ${merge body}

Create expected multi-merge message
    [Arguments]    ${html marker}=*HTML*${SPACE}
    ${header} =    Create expected merge message header    html marker=${html marker}
    ${message 1} =    Create expected merge message body
    ...    FAIL    This test was doomed to fail: again != NO    PASS    ${EMPTY}
    ${message 2} =    Create expected merge old message body
    ...    FAIL    This test was doomed to fail: YES != NO
    Run Keyword And Return    Catenate    SEPARATOR=
    ...    ${header}
    ...    ${message 1}
    ...    <hr>${message 2}

Log should have been created with Fail keywords flattened
    ${log} =    Get File    ${OUTDIR}/log.html
    Should Contain    ${log}    "*Content flattened."
