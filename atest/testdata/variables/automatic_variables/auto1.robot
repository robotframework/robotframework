*** Settings ***
Documentation     This is suite documentation. With ${VARIABLE}.
Metadata          MeTa1    Value
Metadata          meta2    ${VARIABLE}
Suite Setup       Check Variables In Suite Setup    ${EXP_SUITE_NAME}
...               ${EXP_SUITE_DOC}    ${EXP_SUITE_META}
Suite Teardown    Check Variables In Suite Teardown    ${EXP_SUITE_NAME}
...               FAIL    ${EXP_SUITE_STATS}    @{LAST_TEST}
Force Tags        Force 1    include this test
Resource          resource.robot
Library           Collections
Library           HelperLib.py    ${SUITE NAME}    ${SUITE DOCUMENTATION}
...               ${SUITE METADATA}    ${SUITE SOURCE}    ${OPTIONS}

*** Variables ***
${VARIABLE}          variable value
${EXP_SUITE_NAME}    Automatic Variables.Auto1
${EXP_SUITE_DOC}     This is suite documentation. With ${VARIABLE}.
${EXP_SUITE_META}    {'MeTa1': 'Value', 'meta2': '${VARIABLE}'}
${EXP_SUITE_STATS}   17 tests, 15 passed, 2 failed
@{LAST_TEST}         \&{OPTIONS}    PASS

*** Test Cases ***
Previous Test Variables Should Have Default Values
    Check Previous Test Variables

Test Name
    [Setup]       Should Be Equal    ${TEST_NAME}    Test Name
                  Should Be Equal    ${TEST_NAME}    Test Name
    [Teardown]    Should Be Equal    ${TEST_NAME}    Test Name

Test Documentation
    [Documentation]    My doc.
    ...                In 2 lines! And with ${VARIABLE}!!
    [Setup]       Should Be Equal    ${TEST DOCUMENTATION}    My doc.\nIn 2 lines! And with ${VARIABLE}!!
                  Should Be Equal    ${TEST DOCUMENTATION}    My doc.\nIn 2 lines! And with ${VARIABLE}!!
    [Teardown]    Should Be Equal    ${TEST DOCUMENTATION}    My doc.\nIn 2 lines! And with ${VARIABLE}!!

Test Tags
    [Tags]    id-${42}    Hello, world!    ${VARIABLE}
    [Setup]       Check Test Tags    Force 1    Hello, world!    id-42    include this test    ${VARIABLE}
                  Check Test Tags    Force 1    Hello, world!    id-42    include this test    ${VARIABLE}
    [Teardown]    Check Test Tags    Force 1    Hello, world!    id-42    include this test    ${VARIABLE}

Modifying \${TEST TAGS} does not affect actual tags test has
    [Documentation]    The variable is changed but not "real" tags
    [Tags]    mytag
    Append To List    ${TEST TAGS}    not really added
    Check Test Tags    Force 1    include this test    mytag    not really added

Suite Name
    Should Be Equal    ${SUITE_NAME}    ${EXP_SUITE_NAME}

Suite Documentation
    Should Be Equal    ${SUITE_DOCUMENTATION}    ${EXP_SUITE_DOC}

Suite Metadata
    [Setup]    Suite Metadata Should Be Correct    ${EXP_SUITE_META}
    Suite Metadata Should Be Correct    ${EXP_SUITE_META}
    ${expected} =    Evaluate    ${EXP_SUITE_META}
    Should Be Equal    ${SUITE METADATA}    ${expected}
    ${result} =    Create Dictionary    &{SUITE METADATA}
    Should Be Equal    ${result}    ${expected}
    [Teardown]    Suite Metadata Should Be Correct    ${EXP_SUITE_META}

Modifying \&{SUITE METADATA} does not affect actual metadata suite has
    [Documentation]    The variable is changed but not "real" metadata
    Set To Dictionary    ${SUITE METADATA}    Meta1    not really set
    Set To Dictionary    ${SUITE METADATA}    NotSet    not really set
    Suite Metadata Should Be Correct
    ...    {'MeTa1': 'not really set', 'meta2': '${VARIABLE}', 'NotSet': 'not really set'}

Suite Variables Are Available At Import Time
    [Documentation]    Possible variables in them are not resolved, though.
    [Template]         Import time value should be
    source      ${CURDIR}${/}auto1.robot
    name        Automatic Variables.Auto1
    doc         This is suite documentation. With \${VARIABLE}.
    metadata    {'MeTa1': 'Value', 'meta2': '\${VARIABLE}'}
    options     {'include': ['include this test'], 'exclude': ['exclude', 'e2'], 'skip': ['skip_me'], 'skip_on_failure': ['sof']}

Suite Status And Suite Message Are Not Visible In Tests
    Variable Should Not Exist    $SUITE_STATUS
    Variable Should Not Exist    $SUITE_MESSAGE

Test Status Should Not Exist Outside Teardown
    [Setup]    Variable Should Not Exist    $TEST_STATUS
    Variable Should Not Exist    $TEST_STATUS

Test Message Should Not Exist Outside Teardown
    [Setup]    Variable Should Not Exist    $TEST_MESSAGE
    Variable Should Not Exist    $TEST_MESSAGE
    Check Previous Test variables    Test Status Should Not Exist Outside Teardown    PASS

Test Status When Test Fails
    [Documentation]    FAIL Expected failure in test
    Check Previous Test variables    Test Message Should Not Exist Outside Teardown    PASS
    Fail    Expected failure in test
    [Teardown]    Check Test Variables    Test Status When Test Fails    FAIL    Expected failure in test

Test Status When Setup Fails
    [Documentation]    FAIL Setup failed:\nExpected failure in setup
    [Setup]    Fail    Expected failure in setup
    Fail    Should not be executed
    [Teardown]    Check Test Variables    Test Status When Setup Fails    FAIL    Setup failed:\nExpected failure in setup

Previous Test Variables Should Have Correct Values When That Test Fails
    [Setup]    Check Previous Test variables    Test Status When Setup Fails    FAIL    Setup failed:\nExpected failure in setup
    Check Previous Test variables    Test Status When Setup Fails    FAIL    Setup failed:\nExpected failure in setup
    [Teardown]    Check Previous Test variables    Test Status When Setup Fails    FAIL    Setup failed:\nExpected failure in setup

\&{OPTIONS}
    FOR    ${name}    ${expected}    IN
    ...    include    include this test
    ...    exclude    exclude, e2
    ...    skip       Skip Me
    ...    skip_on_failure    s o f
        ${expected} =    Evaluate    $expected.split(', ')
        Should Be Equal    ${OPTIONS.${name}}     ${expected}
        Should Be Equal    ${OPTIONS}[${name}]    ${{[exp.upper() for exp in $expected]}}
        FOR    ${exp}    IN    @{expected}
            Should Contain    ${OPTIONS}[${name}]    ${exp}
            Should Contain    ${OPTIONS.${name}}     ${exp.upper()}
        END
    END
