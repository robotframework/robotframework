*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${FORMATS DIR}     ${DATA DIR}/parsing/data_formats
${TSV DIR}         ${FORMATS DIR}/tsv
${TXT DIR}         ${FORMATS DIR}/txt
${ROBOT DIR}       ${FORMATS DIR}/robot
${REST DIR}        ${FORMATS DIR}/rest
${JSON DIR}        ${FORMATS DIR}/json
${MIXED DIR}       ${FORMATS DIR}/mixed_data
${RESOURCE DIR}    ${FORMATS DIR}/resources
@{SAMPLE TESTS}    Passing    Failing    User Keyword    Nön-äscïï    Own Tags    Default Tags    Variable Table
...                Resource File    Variable File    Library Import    Test Timeout    Keyword Timeout    Empty Rows    Document
...                Default Fixture    Overridden Fixture    Quotes    Escaping
@{SUBSUITE TESTS}    Suite1 Test    Suite2 Test

*** Keywords ***
Previous Run Should Have Been Successful
    Should Not Be Equal    ${SUITE}    ${None}    Running tests failed.    No Values

Run Sample File And Check Tests
    [Arguments]    ${options}    ${path}
    Run Tests    ${options}    ${path}
    ${ignore}    ${type} =    Split Extension    ${path}
    Should Be Equal    ${SUITE.name}    Sample
    Should Be Equal    ${SUITE.doc}    A complex testdata file in ${type} format.
    Check Log Message    ${SUITE.setup.messages[0]}    Setup
    Teardown Should Not Be Defined    ${SUITE}
    Should Contain Tests    ${SUITE}    @{sample_tests}
    Check Test Tags    Own Tags    force1    force2    own1    own2
    Check Test Tags    Default Tags    default1    force1    force2
    ${test} =    Check Test Case    Test Timeout
    Should Be Equal    ${test.timeout}    10 milliseconds
    ${test} =    Check Test Case    Keyword Timeout
    Should Be Equal    ${test.kws[0].timeout}    2 milliseconds
    Check Test Doc    Document    Testing the metadata parsing.
    ${test} =    Check Test Case    Default Fixture
    Setup Should Not Be Defined     ${test}
    Check Log Message    ${test.teardown.messages[0]}    Test Teardown
    ${test} =    Check Test Case    Overridden Fixture
    Check Log Message    ${test.setup.messages[0]}    Own Setup    INFO
    Check Log Message    ${test.teardown.messages[0]}    Failing Teardown    FAIL

Run Suite Dir And Check Results
    [Arguments]    ${options}    ${path}
    Run Tests    ${options}    ${path}
    ${ignore}    ${type} =    Split Path    ${path}
    Should Be Equal    ${SUITE.name}    ${type.capitalize()}
    Should Be Equal    ${SUITE.doc}    ${EMPTY}
    Should Contain Suites    ${SUITE}    Sample    With Init
    Should Contain Suites    ${SUITE.suites[1]}    Sub Suite1    Sub Suite2
    Should Contain Tests    ${SUITE}    @{SAMPLE_TESTS}    @{SUBSUITE_TESTS}
    ${path} =    Normalize Path    ${path}
    IF    $type != 'json'
        Syslog Should Contain    | INFO \ | Data source '${path}${/}invalid.${type}' has no tests or tasks.
        Syslog Should Contain    | INFO \ | Data source '${path}${/}empty.${type}' has no tests or tasks.
    END
    Syslog Should Contain    | INFO \ | Ignoring file or directory '${path}${/}not_a_picture.jpg'.

Check Suite With Init
    [Arguments]    ${suite}
    Should Be Equal    ${suite.name}    With Init
    Should Be Equal    ${suite.doc}    Testing suite init file
    Check Log Message    ${suite.setup.kws[0].messages[0]}    Running suite setup
    Teardown Should Not Be Defined    ${suite}
    Should Contain Suites    ${suite}    Sub Suite1    Sub Suite2
    Should Contain Tests    ${suite}    @{SUBSUITE_TESTS}
