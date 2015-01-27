*** Settings ***
Suite Setup       My Setup
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Cases ***
Test Case Name
    ${tc} =    Check Test Case    lower case test case name
    Should Be Equal    ${tc.name}    lower case test case name
    ${tc} =    Check Test Case    Test Case Documentation
    Should Be Equal    ${tc.name}    Test Case Documentation

Test Case Documentation
    Verify Test Documentation    Documentation for this test case

Test Case Documentation in Multiple Columns
    Verify Test Documentation    Documentation for this test case in multiple columns

Test Case Documentation in Multiple Lines
    Verify Test Documentation    ${1}st line is shortdoc.\nDocumentation for this test case in\nmultiple\nlines

Test Case Documentation With Variables
    Verify Test Documentation    String variables like Robot and number ones like 42 work in documentation

Test Case Documentation With Non-Existing Variables
    Verify Test Documentation
    ...    \${NONEX} variables are just left unchanged in all
    ...    documentations. Existing ones are replaced:
    ...    "10 milliseconds" and 42

Test Case Name and Documentation On Console
    Check Stdout Contains    Test Case Documentation in Multiple Lines :: 1st line is shortdoc.${SPACE * 4}| PASS |

Test Case Tags
    [Documentation]    Check that test case tags can be set in one and multiple lines and that they override Default Tags but not Force Tags
    Check Test Tags    Test Case Tags    force-1    test-1    test-2
    Check Test Tags    Test Case Tags In Multiple Rows    force-1    test-1    test-2    test-3    test-4
    ...    test-5
    Check Test Tags    Test Case Default Tags    default-1    default-2    default-3    force-1

Test Case Tags With Variables
    [Documentation]    Check that variables work in test case tags and invalid variables are handled correctly
    Check Test Tags    Test Case Tags With Variables    force-1    test-1    test-2    test-3    test-4
    ...    test-5

Test Case Tags With Non-Existing Variables is Okay
    Check Test Tags    Test Case Tags With Non-Existing Variables    \${non_existing}    \@{non_existing}    force-1

Test Case Setup
    ${test} =    Check Test Case    Test Case Setup
    Verify Setup    ${test}    BuiltIn.Log    Test case setup

Test Case Setup With Escapes
    ${test} =    Check Test Case    Test Case Setup With Escapes
    Verify Setup    ${test}    BuiltIn.Log    One backslash \\

Test Case Teardown
    ${test} =    Check Test Case    Test Case Teardown
    Verify Teardown    ${test}    BuiltIn.Log    Test case teardown

Test Case Teardown With Escapes
    ${test} =    Check Test Case    Test Case Teardown With Escapes
    Verify Teardown    ${test}    BuiltIn.Log    \${notvar} is not a variable

Test Case Timeout
    Check Test Case    Test Case Timeout
    Check Test Case    Test Case Timeout 2

Test Case Timeout With Variables
    Check Test Case    Test Case Timeout With Variables

Test Case With Invalid Timeout
    Check Test Case    Test Case With Invalid Timeout

Multiple Test Case Metas
    ${test} =    Check Test Case    Multiple Test Case Metas
    Should Be Equal    ${test.doc}    Documentation for this test case
    Should Contain Tags    ${test}    force-1    test-1    test-2
    Verify Setup    ${test}    BuiltIn.Log    Test case setup
    Verify Teardown    ${test}    BuiltIn.Log    Test case teardown

Test Case With Invalid Metadata
    Check Test Case    Test Case With Invalid Metadata
    Check Stderr Contains    [ ERROR ] Error in file '${PATH}': Invalid syntax in test case 'Test Case With Invalid Metadata': Non-existing setting 'Invalid Test Meta'.

Escaping Metadata In Test Case Table
    ${test} =    Check Test Case    Escaping Metadata in Test Case Table
    Should Be Equal    ${test.doc}    Two backslashes \\\\

User Keyword Name
    ${test} =    Check Test Case    Lower Case User Keyword Name
    Should Be Equal    ${test.keywords[0].name}    uk with lower case name
    Should Be Equal    ${test.keywords[1].name}    uk with lower case name
    Should Be Equal    ${test.keywords[2].name}    uk with lower case name

User Keyword Documentation
    ${test} =    Check Test Case    User Keyword Documentation
    Should Be Equal    ${test.keywords[0].doc}    Documentation for a user keyword
    Should Be Equal    ${test.keywords[1].doc}    Documentation in multiple columns

User Keyword Short Documentation
    ${test} =    Check Test Case    User Keyword With Short Documentation
    Should Be Equal    ${test.keywords[0].doc}    This is the short doc and also the only thing logged.

User Keyword Documentation With Variables
    ${test} =    Check Test Case    User Keyword Documentation With Variables
    Should Be Equal    ${test.keywords[0].doc}    Variables work in documentation. For example: Robot and 42

User Keyword Documentation With Non Existing Variables
    ${tc} =    Check Test Case    User Keyword Documentation with non Existing Variables
    Should Be Equal    ${tc.kws[0].doc}    \@{non_existing} variables are left unchanged in docs.

User Keyword Arguments
    ${test} =    Check Test Case    User Keyword Arguments
    Should Be Equal    ${test.keywords[0].args[0]}    one
    Check Log Message    ${test.keywords[0].keywords[0].messages[0]}    one
    Should Be Equal    ${test.keywords[1].args[0]}    one
    Should Be Equal    ${test.keywords[1].args[1]}    two
    Should Be Equal    ${test.keywords[1].args[2]}    three
    Check Log Message    ${test.keywords[1].keywords[0].messages[0]}    one two three

User Keyword Return
    Check Test Case    User Keyword Return

User Keyword Timeout
    Check Test Case    User Keyword Timeout

User Keyword Timeout With Variables
    Check Test Case    User Keyword Timeout With Variables

User Keyword With Invalid Timeout
    Check Test Case    User Keyword With Invalid Timeout

User Keyword With Multiple Metas
    ${test} =    Check Test Case    User Keyword With Multiple Metas
    Should Be Equal    ${test.keywords[0].doc}    Documentation for a user keyword

User Keyword With Invalid Metadata
    Check Test Case    User Keyword With Invalid Metadata
    Check Stderr Contains    [ ERROR ] Error in file '${PATH}': Invalid syntax in keyword 'UK With Invalid Meta Passing': Non-existing setting 'Invalid UK Meta'.
    Check Stderr Contains    [ ERROR ] Error in file '${PATH}': Invalid syntax in keyword 'UK With Invalid Meta Failing': Non-existing setting 'Invalid'.

*** Keywords ***
My Setup
    ${options} =    Catenate
    ...    --variable suite_doc_from_cli:Hello
    ...    --variable suite_setup_from_cli:Log
    ...    --variable suite_teardown_from_cli:Log
    ...    --variable meta_from_cli:my_metadata
    Run Tests    ${options}    core/test_and_uk_settings.robot
    ${PATH} =    Normalize Path    ${DATADIR}/core/test_and_uk_settings.robot
    Set Suite Variable    $PATH

Verify Test Documentation
    [Arguments]    @{doc lines}
    ${tc} =    Check Test Case    ${TEST NAME}
    ${doc} =    Catenate    SEPARATOR=\n    @{doc lines}
    Should Be Equal    ${tc.doc}    ${doc}

Verify Setup
    [Arguments]    ${item}    ${expected_name}    ${expected_message}
    Verify Fixture    ${item.setup}    ${expected_name}    ${expected_message}

Verify Teardown
    [Arguments]    ${item}    ${expected_name}    ${expected_message}
    Verify Fixture    ${item.teardown}    ${expected_name}    ${expected_message}

Verify Fixture
    [Arguments]    ${fixture}    ${expected_name}    ${expected_message}
    Should Be Equal    ${fixture.name}    ${expected_name}
    Check Log Message    ${fixture.messages[0]}    ${expected_message}
