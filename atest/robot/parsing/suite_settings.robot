*** Settings ***
Documentation     Tests for suite settings except for Metadata that is tested
...               in 'suite_metadate.robot' file.
Suite Setup       Run Tests    --variable suite_doc_from_cli:doc_from_cli --variable suite_fixture_from_cli:Log
...               parsing/suite_settings.robot
Resource          atest_resource.robot

*** Test Cases ***
Suite Name
    Should Be Equal    ${SUITE.name}    Suite Settings

Suite Documentation
    ${doc} =    Catenate    SEPARATOR=\n
    ...    1st logical line
    ...    (i.e. paragraph)
    ...    is shortdoc on console.
    ...    ${EMPTY}
    ...    Documentation can have multiple rows
    ...    and also multiple columns.
    ...    Newlines can also be added literally with "\n".
    ...    ${EMPTY}
    ...    Variables work since Robot 1.2 and doc_from_cli works too.
    ...    Starting from RF 2.1 \${nonexisting} variables are left unchanged.
    ...    Escaping (e.g. '\${non-existing}', 'c:\\temp', '\\n') works too.
    Should Be Equal    ${SUITE.doc}    ${doc}

Suite Name And Documentation On Console
    Check Stdout Contains    Suite Settings :: 1st logical line (i.e. paragraph) is shortdoc on console.${SPACE * 3}\n
    Check Stdout Contains    Suite Settings :: 1st logical line (i.e. paragraph) is shortdoc on... | PASS |\n

Test Setup
    ${test} =    Check Test Case    Test Case
    Verify Setup    ${test}    BuiltIn.Log    Default test setup

Test Teardown
    ${test} =    Check Test Case    Test Case
    Verify Teardown    ${test}    BuiltIn.Log    Default test teardown

Force and Default Tags
    Check Test Tags    Test Case    f1    F2    default

Suite Setup
    Verify Setup    ${SUITE}    BuiltIn.Log    Default suite setup

Suite Teardown
    Verify Teardown    ${SUITE}    BuiltIn.Log    Default suite teardown

Deprecated Setting Format
    Verify Error    0
    ...    Setting 'For CET ag S' is deprecated. Use 'Force Tags' instead.
    ...    level=WARN

Invalid Setting
    Verify Error    1    Non-existing setting 'Invalid Setting'.

*** Keywords ***
Verify Setup
    [Arguments]    ${item}    ${expected_name}    ${expected_message}
    Verify Fixture    ${item.setup}    ${expected_name}    ${expected_message}

Verify Teardown
    [Arguments]    ${item}    ${expected_name}    ${expected_message}
    Verify Fixture    ${item.teardown}    ${expected_name}    ${expected_message}

Verify Fixture
    [Arguments]    ${fixture}    ${expected_name}    ${expected_message}
    Should be Equal    ${fixture.name}    ${expected_name}
    Check Log Message    ${fixture.messages[0]}    ${expected_message}

Verify Error
    [Arguments]    ${index}    @{message parts}    ${level}=ERROR
    ${path} =    Normalize Path    ${DATADIR}/parsing/suite_settings.robot
    ${message} =    Catenate    Error in file '${path}':    @{message parts}
    Check Log Message    ${ERRORS}[${index}]    ${message}    ${level}
