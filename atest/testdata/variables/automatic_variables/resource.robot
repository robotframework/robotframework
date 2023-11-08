*** Settings ***
Library    Collections

*** Keywords ***
Check Variables In Suite Setup
    [Arguments]    ${name}    ${doc}    ${meta}    @{prev_test}
    Check Test Variables Do Not Exist
    Check Previous Test Variables    @{prev_test}
    Should Be Equal    ${SUITE_NAME}    ${name}
    Should Be Equal    ${SUITE_DOCUMENTATION}    ${doc}
    Suite Metadata Should Be Correct    ${meta}
    Variable Should Not Exist    $SUITE_STATUS
    Variable Should Not Exist    $SUITE_MESSAGE

Check Variables In Suite Teardown
    [Arguments]    ${name}    ${status}    ${message}    @{prev_test}
    Check Test Variables Do Not Exist
    Check Previous Test Variables    @{prev_test}
    Should Be Equal    ${SUITE_NAME}    ${name}
    Should Be Equal    ${SUITE_STATUS}    ${status}
    Should Be Equal    ${SUITE_MESSAGE}    ${message}

Check Test Variables Do Not Exist
    Variable Should Not Exist    $TEST_NAME
    Variable Should Not Exist    $TEST_STATUS
    Variable Should Not Exist    $TEST_MESSAGE

Check Previous Test Variables
    [Arguments]    ${name}=    ${status}=    ${message}=
    Should Be Equal    ${PREV_TEST_STATUS}    ${status}
    Should Be Equal    ${PREV_TEST_MESSAGE}    ${message}
    Should Be Equal    ${PREV_TEST_NAME}    ${name}

Check Test Variables
    [Arguments]    ${name}    ${status}    ${message}
    Should Be Equal    ${TEST_STATUS}    ${status}
    Should Be Equal    ${TEST_MESSAGE}    ${message}
    Should Be Equal    ${TEST_NAME}    ${name}

Check Test Tags
    [Arguments]    @{expected}
    Log Many    @{TEST TAGS}
    Log Many    @{expected}
    Should Be Equal    ${expected}    ${TEST TAGS}

Suite Metadata Should Be Correct
    [Arguments]    ${expected}
    ${expected} =    Evaluate    ${expected}
    Dictionaries Should Be Equal    ${SUITE METADATA}    ${expected}
