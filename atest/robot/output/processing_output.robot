*** Settings ***
Documentation     Testing reading and processing data from xml outputs generated by Robot or Rebot itself.
Resource          atest_resource.robot

*** Test Cases ***
Test Case File Suite
    [Documentation]    Testing that output file created from simple test case file is correct.
    My Run Robot And Rebot    ${EMPTY}    misc/normal.robot
    Should Be Equal    ${SUITE.name}    Normal
    Should Be Equal    ${SUITE.doc}    Normal test cases
    Should Be Equal    ${SUITE.metadata['Something']}    My Value
    Should Be Equal as Strings    ${SUITE.metadata}    {Something: My Value}
    Check Normal Suite Defaults    ${SUITE}
    Should Be Equal    ${SUITE.full_message}    2 tests, 2 passed, 0 failed
    Should Be Equal    ${SUITE.statistics.message}    2 tests, 2 passed, 0 failed
    Should Contain Tests    ${SUITE}    First One    Second One

Directory Suite
    [Documentation]    Testing suite created from a test suite directory. Also testing metadata from cli.
    My Run Robot And Rebot    --metadata x:y -M a:b --name "My Name" --doc Something    misc/suites
    Should Be Equal    ${SUITE.name}    My Name
    Should Be Equal    ${SUITE.doc}    Something
    Should Be Equal    ${SUITE.metadata['x']}    y
    Should Be Equal    ${SUITE.metadata['a']}    b
    Should Be True    list($SUITE.metadata.items()) == [('a', 'b'), ('x', 'y')]
    Check Suite Got From misc/suites/ Directory

Minimal hand-created output
    [Documentation]    Testing minimal hand created suite with tests or subsuites
    Run Rebot    --log log_from_created_output.html    rebot/created_normal.xml
    File Should Not Be Empty    ${OUTDIR}/log_from_created_output.html
    Check Names    ${SUITE}    Root
    Should Contain Suites    ${SUITE}    Sub 1    Sub 2
    Check Names    ${SUITE.suites[0]}    Sub 1    Root.
    Check Names    ${SUITE.suites[1]}    Sub 2    Root.
    Check Minimal Suite Defaults    ${SUITE}
    Check Minimal Suite Defaults    ${SUITE.suites[0]}
    Check Minimal Suite Defaults    ${SUITE.suites[1]}
    Should Contain Tests    ${SUITE}    Test 1.1    Test 1.2    Test 2.1
    Check Names    ${SUITE.suites[0].tests[0]}    Test 1.1    Root.Sub 1.
    Check Names    ${SUITE.suites[0].tests[1]}    Test 1.2    Root.Sub 1.
    Check Names    ${SUITE.suites[1].tests[0]}    Test 2.1    Root.Sub 2.

*** Keywords ***
My Run Robot And Rebot
    [Arguments]    ${params}    ${paths}
    Run Tests Without Processing Output    ${params}    ${paths}
    Copy Previous Outfile
    Run Rebot    ${EMPTY}    ${OUTFILE COPY}

Check Normal Suite Defaults
    [Arguments]    ${suite}    ${message}=    ${setup}=${None}    ${teardown}=${None}
    Log    ${suite.name}
    Check Suite Defaults    ${suite}    ${message}    ${setup}    ${teardown}
    Check Normal Suite Times    ${suite}

Check Minimal Suite Defaults
    [Arguments]    ${suite}    ${message}=
    Check Suite Defaults    ${suite}    ${message}
    Check Minimal Suite Times    ${suite}

Check Normal Suite Times
    [Arguments]    ${suite}
    Timestamp Should Be Valid    ${suite.starttime}
    Timestamp Should Be Valid    ${suite.endtime}
    Elapsed Time Should Be Valid    ${suite.elapsedtime}
    Should Be True    ${suite.elapsedtime} >= 1

Check Minimal Suite Times
    [Arguments]    ${suite}
    Should Be Equal    ${suite.starttime}      ${NONE}
    Should Be Equal    ${suite.endtime}        ${NONE}
    Should Be Equal    ${suite.elapsedtime}    ${0}

Check Suite Defaults
    [Arguments]    ${suite}    ${message}=    ${setup}=${None}    ${teardown}=${None}
    Should Be Equal    ${suite.message}          ${message}
    Should Be Equal    ${suite.setup.name}       ${setup}
    Should Be Equal    ${suite.teardown.name}    ${teardown}

Check Suite Got From Misc/suites/ Directory
    Check Normal Suite Defaults    ${SUITE}    teardown=BuiltIn.Log
    Should Be Equal    ${SUITE.status}    FAIL
    Should Contain Suites    ${SUITE}    Suite With Prefix    Fourth    Subsuites
    ...    Custom name for 📂 'subsuites2'    Suite With Double Underscore
    ...    Tsuite1    Tsuite2    Tsuite3
    Should Be Empty    ${SUITE.tests}
    Should Contain Suites    ${SUITE.suites[2]}    Sub1    Sub2
    FOR    ${s}    IN
    ...    ${SUITE.suites[1]}
    ...    ${SUITE.suites[2].suites[0]}
    ...    ${SUITE.suites[2].suites[1]}
    ...    ${SUITE.suites[3].suites[0]}

    ...    ${SUITE.suites[5]}
    ...    ${SUITE.suites[6]}
        Should Be Empty    ${s.suites}
    END
    Should Contain Tests    ${SUITE}
    ...    Test With Prefix
    ...    SubSuite1 First
    ...    SubSuite2 First
    ...    SubSuite3 First
    ...    SubSuite3 Second
    ...    Suite1 First
    ...    Suite1 Second    Third In Suite1    Suite2 First
    ...    Suite3 First
    ...    Suite4 First
    ...    Test With Double Underscore
    ...    Test From Sub Suite 4
    Check Normal Suite Defaults    ${SUITE.suites[0]}
    Check Normal Suite Defaults    ${SUITE.suites[1]}    setup=BuiltIn.Log    teardown=BuiltIn.Log
    Check Normal Suite Defaults    ${SUITE.suites[2]}
    Check Normal Suite Defaults    ${SUITE.suites[2].suites[0]}    setup=Setup    teardown=BuiltIn.No Operation
    Check Normal Suite Defaults    ${SUITE.suites[2].suites[1]}
    Check Normal Suite Defaults    ${SUITE.suites[3].suites[0]}
    Check Normal Suite Defaults    ${SUITE.suites[4]}
    Check Normal Suite Defaults    ${SUITE.suites[4].suites[0]}
    Check Normal Suite Defaults    ${SUITE.suites[5]}
    Check Normal Suite Defaults    ${SUITE.suites[6]}
