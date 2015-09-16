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
    ...    1st line is shortdoc.
    ...    Text from multiple columns is catenated with spaces,
    ...    and line continuation creates a new line.
    ...    Newlines can also be added literally "\n\n".
    ...    Variables work since Robot 1.2 and doc_from_cli works too.
    ...    Starting from RF 2.1 \${nonexisting} variables are left unchanged.
    ...    Escaping (e.g. '\${non-existing}', 'c:\\temp', '\\n') works too.
    ...    For backwards compatibility reasons we still support 'Document'
    ...    setting name and continuing the doc by just repeating the setting multiple times.
    Should Be Equal    ${SUITE.doc}    ${doc}

Suite Name And Documentation On Console
    Check Stdout Contains    Suite Settings :: 1st line is shortdoc.${SPACE * 39}\n
    Check Stdout Contains    Suite Settings :: 1st line is shortdoc.${SPACE * 31}| PASS |\n

Test Setup
    ${test} =    Check Test Case    Test Case
    Verify Setup    ${test}    BuiltIn.Log    Default test setup

Test Teardown
    ${test} =    Check Test Case    Test Case
    Verify Teardown    ${test}    BuiltIn.Log    Default test teardown

Suite Setup
    Verify Setup    ${SUITE}    BuiltIn.Log    Default suite setup

Suite Teardown
    Verify Teardown    ${SUITE}    BuiltIn.Log    Default suite teardown

Invalid Setting
    ${path} =    Normalize Path    ${DATADIR}/parsing/suite_settings.robot
    Check Log Message    ${ERRORS[4]}
    ...    Error in file '${path}': Non-existing setting 'Invalid Setting'.    ERROR

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
