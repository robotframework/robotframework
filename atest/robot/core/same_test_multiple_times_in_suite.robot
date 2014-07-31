*** Setting ***
Suite Setup       Run Tests    --exclude exclude    core/same_test_multiple_times_in_suite.txt
Force Tags        pybot    jybot    regression
Resource          atest_resource.txt

*** Test Case ***
Tests With Same Name Should Be Executed
    Check Suite Contains Tests    ${SUITE}    Same Test Multiple Times    Same Test Multiple Times    Same Test Multiple Times    Same Test With Different Case And Spaces    SameTestwith Different CASE and s p a c e s
    ...    Same Test In Data But Only One Executed

There Should Be Warning When Multiple Tests With Same Name Are Executed
    Check Log Message    ${ERRORS[0]}    Multiple test cases with name 'Same Test Multiple Times' executed in test suite 'Same Test Multiple Times In Suite'.    WARN
    Check Log Message    ${ERRORS[1]}    Multiple test cases with name 'Same Test Multiple Times' executed in test suite 'Same Test Multiple Times In Suite'.    WARN
    Check Log Message    ${ERRORS[2]}    Multiple test cases with name 'SameTestwith Different CASE and s p a c e s' executed in test suite 'Same Test Multiple Times In Suite'.    WARN

There Should Be No Warning When There Are Multiple Tests With Same Name In Data But Only One Is Executed
    ${tc} =    Check Test Case    Same Test In Data But Only One Executed
    Check Log Message    ${tc.kws[0].msgs[0]}    This is executed!
    Length Should Be    ${ERRORS}    3
