*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    output/Logging_control.robot
Resource         atest_resource.robot

*** Test Cases ***
Test Flattened keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Should be equal as strings    ${tc.kws[0].messages[0]}    This text should show under Log within the test, Flattened keyword should not be visible
    Should Be Equal    ${tc.kws[0].name}    BuiltIn.Log

Test removed keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    ${kw}=    Set variable    ${tc.kws[0].keywords[0]}
    Should be equal    ${tc.kws[0].name}    Higher keyword
    Should be equal    ${kw.name}    BuiltIn.Log
    Should be equal as strings    ${kw.messages[0]}    This text should show under Log, but the removed keyword and text is nowhere to be seen

Test reduced keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Should be equal    ${tc.kws[0].name}    Reduced keyword
    Should be equal as strings    ${tc.kws[0].messages[0]}    This text should show under reduced keyword, not under Log

Protection against premature flattening
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal as strings  ${ERRORS.msgs[0]}    Message from outside of any keyword in test "Protection against premature flattening"\nThis text should show under reduced keyword, not under Log
    Should be empty    ${tc.kws}
