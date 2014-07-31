*** Settings ***
Suite Setup     My Setup
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***
Suite Name
    Should Be Equal  ${suite.name}  Suite Settings

Suite Documentation
    [Documentation]  Checks that suite document can be set in metadata. Also checks that backslashes are escaped correctly.
    Should Be Equal  ${suite.doc}  Test cases for metadata in Setting table (incl. imports) and within Test Case and Keyword tables. Text from multiple columns is catenated with spaces, and line continuation creates a new line. Real newlines can be added with 'backslash+n' (e.g. '\n'). Also variables work since Robot 1.2, and they work from commandline too: Hello.\nStarting from RF 2.1 \${nonexisting} variables are just left unchanged.\nOf course escaping (e.g. '\${non-existing-in-suite-doc}' and '\\') works too.

Suite Test Setup
    ${test} =  Check Test Case  Test Case
    Verify Setup  ${test}  BuiltIn.Log  Default test setup

Suite Test Teardown
    ${test} =  Check Test Case  Test Case
    Verify Teardown  ${test}  BuiltIn.Log  Default test teardown

Suite Suite Setup
    Verify Setup  ${suite}  BuiltIn.Log  Default suite setup

Suite Suite Teardown
    Verify Teardown  ${suite}  BuiltIn.Log  Default suite teardown


*** Keywords ***
My Setup
    Run Tests  --variable suite_doc_from_cli:Hello --variable suite_fixture_from_cli:Log  core/suite_settings.txt

Verify Setup
    [Arguments]  ${item}  ${expected_name}  ${expected_message}
    Verify Fixture  ${item.setup}  ${expected_name}  ${expected_message}

Verify Teardown
    [Arguments]  ${item}  ${expected_name}  ${expected_message}
    Verify Fixture  ${item.teardown}  ${expected_name}  ${expected_message}

Verify Fixture
    [Arguments]  ${fixture}  ${expected_name}  ${expected_message}
    Should be Equal  ${fixture.name}  ${expected_name}
    Check Log Message  ${fixture.messages[0]}  ${expected_message}

