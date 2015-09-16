*** Setting ***
Suite Setup       Run Tests    --exclude exclude    core/same_test_multiple_times_in_suite.robot
Resource          atest_resource.robot

*** Test Case ***
Tests With Same Name Should Be Executed
    Should Contain Tests    ${SUITE}
    ...    Same Test Multiple Times
    ...    Same Test Multiple Times
    ...    Same Test Multiple Times
    ...    Same Test With Different Case And Spaces
    ...    SameTestwith Different CASE and s p a c e s
    ...    Same Test In Data But Only One Executed

There Should Be Warning When Multiple Tests With Same Name Are Executed
    Check Multiple Tests Log Message    ${ERRORS[0]}    Same Test Multiple Times
    Check Multiple Tests Log Message    ${ERRORS[1]}    Same Test Multiple Times
    Check Multiple Tests Log Message    ${ERRORS[2]}    SameTestwith Different CASE and s p a c e s

There Should Be No Warning When There Are Multiple Tests With Same Name In Data But Only One Is Executed
    ${tc} =    Check Test Case    Same Test In Data But Only One Executed
    Check Log Message    ${tc.kws[0].msgs[0]}    This is executed!
    Length Should Be    ${ERRORS}    3

*** Keywords ***
Check Multiple Tests Log Message
    [Arguments]    ${error}    ${test}
    ${message} =    Catenate    Multiple test cases with name '${test}'
    ...    executed in test suite 'Same Test Multiple Times In Suite'.
    Check Log Message    ${error}    ${message}    WARN
