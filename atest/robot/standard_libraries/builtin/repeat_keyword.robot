*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/repeat_keyword.robot
Resource          atest_resource.robot

*** Test Cases ***
Times As String
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc.kws[0]}    2    Hello, repeating world!

Times As Integer
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc.kws[0]}    42    This works too!!

Times With 'times' Postfix
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc.kws[0]}    3    This is done 3 times
    Check Repeated Messages    ${tc.kws[1]}    2    Case and space insensitive

Times With 'x' Postfix
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc.kws[0]}    10    Close to old repeating syntax
    Check Repeated Messages    ${tc.kws[1]}    1    Case and space

Zero And Negative Times
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc.kws[0]}    0
    Check Repeated Messages    ${tc.kws[2]}    0
    Check Repeated Messages    ${tc.kws[3]}    0

Invalid Times
    Check Test Case    Invalid Times 1
    Check Test Case    Invalid Times 2

Repeat Keyword With Time String
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages With Time    ${tc.kws[0]}    This is done for 00:00:00.003
    Check Repeated Messages With Time    ${tc.kws[1]}    This is done for 3 milliseconds
    Check Repeated Messages With Time    ${tc.kws[2]}    This is done for 3ms

Repeat Keyword Arguments As Variables
    ${tc} =    Check Test Case    ${TEST_NAME}
    Check Repeated Keyword Name    ${tc.kws[1]}    2    BuiltIn.Should Be Equal
    Check Repeated Keyword Name    ${tc.kws[3]}    42    BuiltIn.Should Be Equal
    Check Repeated Keyword Name    ${tc.kws[5]}    10    BuiltIn.No Operation
    Check Repeated Keyword Name    ${tc.kws[7]}    1    BuiltIn.Should Be Equal

Repeated Keyword As Non-existing Variable
    Check Test Case    ${TEST_NAME}

Argument To Repeated Keyword As Non-existing Variable
    Check Test Case    ${TEST_NAME}

Repeated Keyword Failing
    Check Test Case    Repeated Keyword Failing Immediately
    Check Test Case    Repeated Keyword Failing On Third Round

Repeat Keyword With Continuable Failure
    ${tc} =    Check Test Case    ${TEST_NAME}
    Length Should Be    ${tc.kws[0].kws}    3

Repeat Keyword With Failure After Continuable Failure
    ${tc} =    Check Test Case    ${TEST_NAME}
    Length Should Be    ${tc.kws[0].kws}    2

Repeat Keyword With Pass Execution
    ${tc} =    Check Test Case    ${TEST_NAME}
    Length Should Be    ${tc.kws[0].kws}    1

Repeat Keyword With Pass Execution After Continuable Failure
    ${tc} =    Check Test Case    ${TEST_NAME}
    Length Should Be    ${tc.kws[0].kws}    2

*** Keywords ***
Check Repeated Messages
    [Arguments]    ${kw}    ${count}    ${msg}=${None}
    Should Be Equal As Integers    ${kw.kw_count}    ${count}
    FOR    ${i}    IN RANGE    ${count}
        Check Log Message    ${kw.msgs[${i}]}    Repeating keyword, round ${i+1}/${count}.
        Check Log Message    ${kw.kws[${i}].msgs[0]}    ${msg}
    END
    Run Keyword If    ${count} == 0    Check Log Message    ${kw.msgs[0]}    Keyword 'This is not executed' repeated zero times.
    Run Keyword If    ${count} != 0    Should Be Equal As Integers    ${kw.msg_count}    ${count}

Check Repeated Messages With Time
    [Arguments]    ${kw}    ${msg}=${None}
    Should Be True    ${kw.kw_count} > 0
    FOR    ${i}    IN RANGE    ${kw.kw_count}
        Check Log Message    ${kw.msgs[${i}]}
        ...    Repeating keyword, round ${i+1}, *remaining.    pattern=yes
        Check Log Message    ${kw.kws[${i}].msgs[0]}    ${msg}
    END
    Should Be Equal As Integers    ${kw.msg_count}    ${kw.kw_count}

Check Repeated Keyword Name
    [Arguments]    ${kw}    ${count}    ${name}=${None}
    Should Be Equal As Integers    ${kw.kw_count}    ${count}
    FOR    ${i}    IN RANGE    ${count}
        Should Be Equal    ${kw.kws[${i}].name}    ${name}
    END
