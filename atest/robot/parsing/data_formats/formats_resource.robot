*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${FORMATS DIR}     ${DATA DIR}/parsing/data_formats
${HTML DIR}        ${FORMATS DIR}/html
${TSV DIR}         ${FORMATS DIR}/tsv
${TXT DIR}         ${FORMATS DIR}/txt
${ROBOT DIR}       ${FORMATS DIR}/robot
${REST DIR}        ${FORMATS DIR}/rest
${REST DIR 2}      ${FORMATS DIR}/rest_directives
${MIXED DIR}       ${FORMATS DIR}/mixed_data
${RESOURCE DIR}    ${FORMATS DIR}/resources
@{SAMPLE TESTS}    Passing    Failing    User Keyword    Nön-äscïï    Own Tags    Default Tags    Variable Table
...                Resource File    Variable File    Library Import    Test Timeout    Keyword Timeout    Empty Rows    Document
...                Default Fixture    Overridden Fixture    Quotes    Escaping
@{SUBSUITE TESTS}    Suite1 Test    Suite2 Test

*** Keywords ***
Previous Run Should Have Been Successful
    Should Not Be Equal    ${SUITE}    ${None}    Running tests failed.    No Values

Run Tests And Verify Status
    [Arguments]    ${options}    ${paths}
    Set Suite Variable    $SUITE    ${None}
    Run Tests    ${options}    ${paths}
    Previous Run Should Have Been Successful

Run Sample File And Check Tests
    [Arguments]    ${options}    ${path}
    Run Tests And Verify Status    ${options}    ${path}
    ${ignore}    ${type} =    Split Extension    ${path}
    Should Be Equal    ${SUITE.name}    Sample
    Should Be Equal    ${SUITE.doc}    A complex testdata file in ${type} format.
    Check Log Message    ${SUITE.setup.messages[0]}    Setup
    Should Be Equal    ${SUITE.teardown}    ${None}
    Should Contain Tests    ${SUITE}    @{sample_tests}
    Check Test Tags    Own Tags    force1    force2    own1    own2
    Check Test Tags    Default Tags    default1    force1    force2
    ${test} =    Check Test Case    Test Timeout
    Should Be Equal    ${test.timeout}    10 milliseconds
    ${test} =    Check Test Case    Keyword Timeout
    Should Be Equal    ${test.kws[0].timeout}    2 milliseconds
    Check Test Doc    Document    Testing the metadata parsing.
    ${test} =    Check Test Case    Default Fixture
    Should Be Equal    ${test.setup}    ${None}
    Check Log Message    ${test.teardown.messages[0]}    Test Teardown
    ${test} =    Check Test Case    Overridden Fixture
    Check Log Message    ${test.setup.messages[0]}    Own Setup    INFO
    Check Log Message    ${test.teardown.messages[0]}    Failing Teardown    FAIL

Run Suite Dir And Check Results
    [Arguments]    ${options}    ${path}
    Run Tests And Verify Status    ${options}    ${path}
    ${ignore}    ${type} =    Split Path    ${path}
    Should Be Equal    ${SUITE.name}    ${type.capitalize()}
    Should Be Equal    ${SUITE.doc}    ${EMPTY}
    Should Contain Suites    ${SUITE}    Sample    With Init
    Should Contain Suites    ${SUITE.suites[1]}    Sub Suite1    Sub Suite2
    Should Contain Tests    ${SUITE}    @{SAMPLE_TESTS}    @{SUBSUITE_TESTS}
    ${path} =    Normalize Path    ${path}
    Check Syslog Contains    | INFO \ | Data source '${path}${/}invalid.${type}' has no tests or tasks.
    Check Syslog Contains    | INFO \ | Data source '${path}${/}empty.${type}' has no tests or tasks.
    Check Syslog Contains    | INFO \ | Ignoring file or directory '${path}${/}not_a_picture.jpg'.
    Run Keyword If    "${type}" not in ("html", "rest")
    ...    Check Syslog Contains    | ERROR | Parsing '${path}${/}invalid_encoding.${type}' failed: UnicodeDecodeError

Check Suite With Init
    [Arguments]    ${suite}
    Should Be Equal    ${suite.name}    With Init
    Should Be Equal    ${suite.doc}    Testing suite init file
    Check Log Message    ${suite.setup.kws[0].messages[0]}    Running suite setup
    Should Be Equal    ${suite.teardown}    ${None}
    Should Contain Suites    ${suite}    Sub Suite1    Sub Suite2
    Should Contain Tests    ${suite}    @{SUBSUITE_TESTS}

*** Keywords ***
Check HTML Deprecation Message
    [Arguments]    ${index}    ${path}
    ${path} =    Normalize Path    ${path}
    ${msg} =    Catenate
    ...    Using test data in HTML format is deprecated.
    ...    Convert '${path}' to plain text format.
    Check Log Message    @{ERRORS}[${index}]    ${msg}    WARN

Check Automatic Parsing Deprecated Message
    [Arguments]    ${index}    ${path}
    ${path} =    Normalize Path    ${path}
    ${msg} =    Catenate
    ...    Automatically parsing other than '*.robot' files is deprecated.
    ...    Convert '${path}' to '*.robot' format or use '--extension' to
    ...    explicitly configure which files to parse.
    Check Log Message    @{ERRORS}[${index}]    ${msg}    WARN
