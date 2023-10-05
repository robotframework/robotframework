*** Settings ***
Documentation     Tests for suite settings except for Metadata that is tested
...               in 'suite_metadate.robot' file.
Suite Setup       Run Tests    --variable suite_doc_from_cli:doc_from_cli --variable suite_fixture_from_cli:Log
...               parsing/suite_settings.robot
Resource          atest_resource.robot

*** Test Cases ***
Suite Name
    Should Be Equal    ${SUITE.name}    Custom name

Suite Documentation
    ${doc} =    Catenate    SEPARATOR=\n
    ...    1st logical line
    ...    (i.e. paragraph)
    ...    is shortdoc on console.
    ...
    ...    Documentation can have multiple rows
    ...    and${SPACE*4}also${SPACE*4}multiple${SPACE*4}columns.
    ...
    ...    Newlines can also be added literally with "\n".
    ...    If a row ends with a newline
    ...    or backslash no automatic newline is added.
    ...
    ...    | table | =header= |
    ...    | foo${SPACE*3}|${SPACE*4}bar${SPACE*3}|
    ...    | ragged |
    ...
    ...    Variables work since Robot 1.2 and doc_from_cli works too.
    ...    Starting from RF 2.1 \${nonexisting} variables are left unchanged.
    ...    Escaping (e.g. '\${non-existing}', 'c:\\temp', '\\n') works too.
    ...    Not \${closed
    Should Be Equal    ${SUITE.doc}    ${doc}

Suite Name And Documentation On Console
    Stdout Should Contain    Custom name :: 1st logical line (i.e. paragraph) is shortdoc on console.${SPACE * 6}\n
    Stdout Should Contain    Custom name :: 1st logical line (i.e. paragraph) is shortdoc on co... | PASS |\n

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

Invalid Setting
    Error In File    0    parsing/suite_settings.robot    32
    ...    Non-existing setting 'Invalid Setting'.

Small typo should provide recommendation.
    Error In File    1    parsing/suite_settings.robot    33
    ...    SEPARATOR=\n
    ...    Non-existing setting 'Megadata'. Did you mean:
    ...    ${SPACE*4}Metadata

*** Keywords ***
Verify Setup
    [Arguments]    ${item}    ${expected_name}    ${expected_message}
    Verify Fixture    ${item.setup}    ${expected_name}    ${expected_message}

Verify Teardown
    [Arguments]    ${item}    ${expected_name}    ${expected_message}
    Verify Fixture    ${item.teardown}    ${expected_name}    ${expected_message}

Verify Fixture
    [Arguments]    ${fixture}    ${expected_name}    ${expected_message}
    Should be Equal    ${fixture.full_name}    ${expected_name}
    Check Log Message    ${fixture.messages[0]}    ${expected_message}
