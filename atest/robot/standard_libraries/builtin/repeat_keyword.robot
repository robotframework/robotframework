*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/repeat_keyword.robot
Resource          atest_resource.robot

*** Test Cases ***
Times As String
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc[0]}     2    Hello, repeating world!

Times As Integer
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc[0]}    42    This works too!!

Times With 'times' Postfix
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc[0]}     3    This is done 3 times
    Check Repeated Messages    ${tc[1]}     2    Case and space insensitive

Times With 'x' Postfix
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc[0]}    10    Close to old repeating syntax
    Check Repeated Messages    ${tc[1]}     1    Case and space

Zero And Negative Times
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages    ${tc[0]}     0    name=This is not executed
    Check Repeated Messages    ${tc[2]}     0    name=\${name}
    Check Repeated Messages    ${tc[3]}     0    name=This is not executed

Invalid Times
    Check Test Case    Invalid Times 1
    Check Test Case    Invalid Times 2

Repeat Keyword With Time String
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Repeated Messages With Time    ${tc[0]}    This is done for 00:00:00.003
    Check Repeated Messages With Time    ${tc[1]}    This is done for 3 milliseconds
    Check Repeated Messages With Time    ${tc[2]}    This is done for 3ms

Repeat Keyword Arguments As Variables
    ${tc} =    Check Test Case    ${TEST_NAME}
    Check Repeated Keyword Name    ${tc[1]}     2    BuiltIn.Should Be Equal
    Check Repeated Keyword Name    ${tc[3]}    42    BuiltIn.Should Be Equal
    Check Repeated Keyword Name    ${tc[5]}    10    BuiltIn.No Operation
    Check Repeated Keyword Name    ${tc[7]}     1    BuiltIn.Should Be Equal

Repeated Keyword As Non-existing Variable
    Check Test Case    ${TEST_NAME}

Argument To Repeated Keyword As Non-existing Variable
    Check Test Case    ${TEST_NAME}

Repeated Keyword Failing
    Check Test Case    Repeated Keyword Failing Immediately
    Check Test Case    Repeated Keyword Failing On Third Round

Repeat Keyword With Continuable Failure
    ${tc} =    Check Test Case    ${TEST_NAME}
    Length Should Be    ${tc[0].body}        6
    Length Should Be    ${tc[0].messages}    3

Repeat Keyword With Failure After Continuable Failure
    ${tc} =    Check Test Case    ${TEST_NAME}
    Length Should Be    ${tc[0].body}        4
    Length Should Be    ${tc[0].messages}    2

Repeat Keyword With Pass Execution
    ${tc} =    Check Test Case    ${TEST_NAME}
    Length Should Be    ${tc[0].body}        2
    Length Should Be    ${tc[0].messages}    1

Repeat Keyword With Pass Execution After Continuable Failure
    ${tc} =    Check Test Case    ${TEST_NAME}
    Length Should Be    ${tc[0].body}        4
    Length Should Be    ${tc[0].messages}    2

*** Keywords ***
Check Repeated Messages
    [Arguments]    ${kw}    ${rounds}    ${msg}=    ${name}=
    IF    ${rounds} == 0
        Length Should Be     ${kw.body}        1
        Check Log Message    ${kw[0]}          Keyword '${name}' repeated zero times.
    ELSE
        Length Should Be     ${kw.body}        ${{int($rounds) * 2}}
        Length Should Be     ${kw.messages}    ${rounds}
    END
    FOR    ${i}    IN RANGE    ${rounds}
        Check Log Message    ${kw[${i * 2}]}           Repeating keyword, round ${i+1}/${rounds}.
        Check Log Message    ${kw[${i * 2 + 1}, 0]}    ${msg}
    END

Check Repeated Messages With Time
    [Arguments]    ${kw}    ${msg}=${None}
    Should Be True    len($kw.body) / 2 == len($kw.messages) and len($kw.body) > 0
    FOR    ${i}    IN RANGE    ${{len($kw.messages)}}
        Check Log Message    ${kw[${i * 2}]}
        ...    Repeating keyword, round ${i+1}, *remaining.    pattern=yes
        Check Log Message    ${kw[${i * 2 + 1}, 0]}    ${msg}
    END
    Should Be Equal    ${{len($kw.messages) * 2}}    ${{len($kw.body)}}

Check Repeated Keyword Name
    [Arguments]    ${kw}    ${count}    ${name}=${None}
    Should Be True    len($kw.body) / 2 == len($kw.messages) == ${count}
    FOR    ${i}    IN RANGE    1    ${count} * 2    2
        Should Be Equal    ${kw[${i}].full_name}    ${name}
    END
