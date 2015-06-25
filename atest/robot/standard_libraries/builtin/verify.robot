*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/builtin/verify.robot
Force Tags        regression
Default Tags      jybot    pybot
Resource          atest_resource.robot

*** Test Cases ***
Should Not Be True
    Check test case    ${TESTNAME}

Should Not Be True With Message
    Check test case    ${TESTNAME}

Should Not Be True With Invalid Expression
    Check test case    ${TESTNAME}

Should Be True
    Check test case    ${TESTNAME}

Should Be True With Message
    Check test case    ${TESTNAME}

Should Be True With Invalid Expression
    Check test case    ${TESTNAME}

Should (Not) Be True is evaluated with os- and sys-modules
    Check test case    ${TESTNAME}

Should (Not) Be True is evaluated with robot's variables
    Check test case    ${TESTNAME}

Should Not Be Equal
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    unicode
    Verify argument type message    ${tc.kws[1].msgs[0]}    unicode    int
    Verify argument type message    ${tc.kws[2].msgs[0]}    unicode    unicode

Should Not Be Equal with bytes containing non-ascii characters
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    str    str
    Verify argument type message    ${tc.kws[1].msgs[0]}    str    unicode
    Verify argument type message    ${tc.kws[2].msgs[0]}    str    str

Should Be Equal
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    unicode
    Verify argument type message    ${tc.kws[1].msgs[0]}    int    int
    Verify argument type message    ${tc.kws[2].msgs[0]}    str    str
    Verify argument type message    ${tc.kws[3].msgs[0]}    unicode    unicode

Should Be Equal fails with values
    Check test case    ${TESTNAME}

Should Be Equal fails without values
    Check test case    ${TESTNAME}

Should Be Equal with bytes containing non-ascii characters
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    str    str
    Verify argument type message    ${tc.kws[1].msgs[0]}    str    str

Should Be Equal with unicode and bytes with non-ascii characters
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    str    unicode
    Verify argument type message    ${tc.kws[1].msgs[0]}    str    unicode

Should Be Equal When Types Differ But String Representations Are Same
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    int

Should Not Be Equal As Integers
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    unicode

Should Not Be Equal As Integers With Base
    Check test case    ${TESTNAME}

Should Be Equal As Integers
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    unicode

Should Be Equal As Integers With Base
    Check test case    ${TESTNAME}

Should Not Be Equal As Numbers
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    unicode

Should Not Be Equal As Numbers With Precision
    Check test case    ${TESTNAME}

Should Be Equal As Numbers
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    unicode

Should Be Equal As Numbers With Precision
    Check test case    ${TESTNAME}

Should Not Be Equal As Strings
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    unicode    float

Should Be Equal As Strings
    ${tc}=    Check test case    ${TESTNAME}
    Verify argument type message    ${tc.kws[0].msgs[0]}    int    unicode

Should Not Start With
    Check test case    ${TESTNAME}

Should Start With
    Check test case    ${TESTNAME}

Should Start With without values
    Check test case    ${TESTNAME}

Should Not End With
    Check test case    ${TESTNAME}

Should End With
    Check test case    ${TESTNAME}

Should End With without values
    Check test case    ${TESTNAME}

Should Not Contain
    Check test case    ${TESTNAME}

Should Not Contain With Non-String Values
    Check test case    ${TESTNAME}

Should Contain
    Check test case    ${TESTNAME}

Should Contain With Non-String Values
    Check test case    ${TESTNAME}

Should Not Match
    Check test case    ${TESTNAME}

Should Match
    Check test case    ${TESTNAME}

Should Match with bytes containing non-ascii characters
    Check test case    ${TESTNAME}

Should Not Match Regexp
    Check test case    ${TESTNAME}

Should Match Regexp
    Check test case    ${TESTNAME}

Should Match Regexp with bytes containing non-ascii characters
    Check test case    ${TESTNAME}

Should Match Regexp Returns Match And Groups
    Check test case    ${TESTNAME}

Get Length
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Length is 0
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Length is 1
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    Length is 2
    Check Log Message    ${tc.kws[3].kws[0].msgs[0]}    Length is 3
    Check Log Message    ${tc.kws[4].kws[0].msgs[0]}    Length is 11
    Check Log Message    ${tc.kws[5].kws[0].msgs[0]}    Length is 0

Length Should Be
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[-1].msgs[0]}    Length is 2
    Check Log Message    ${tc.kws[-1].msgs[1]}    Length of '*' should be 3 but is 2.    FAIL    pattern=yep
    Check Log Message    ${tc.kws[-1].msgs[2]}    Traceback*    DEBUG    pattern=yep
    Length Should Be    ${tc.kws[-1].msgs}    3

Length Should Be With Non Default Message
    Check Test Case    ${TESTNAME}

Length Should Be With Invalid Length
    Check Test Case    ${TESTNAME}

Should Be Empty
    Check test case    ${TESTNAME}

Should Be Empty With Non Default Message
    Check test case    ${TESTNAME}

Should Not Be Empty
    Check test case    ${TESTNAME}

Should Not Be Empty With Non Default Message
    Check test case    ${TESTNAME}

Length With Length Method
    Check test case    ${TESTNAME}

Length With Size Method
    Check test case    ${TESTNAME}

Length With Length Attribute
    Check test case    ${TESTNAME}

Length Of Java Types
    [Documentation]    Tests that it's possible to get the lenght of String, Vector, Hashtable and array
    [Tags]    jybot
    Check test case    ${TESTNAME}

Should Contain X Times With String
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Item found from the first item 2 times
    Check Log Message    ${tc.kws[1].msgs[0]}    Item found from the first item 1 time
    Check Log Message    ${tc.kws[3].msgs[0]}    Item found from the first item 0 times

Should Contain X Times With List
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Item found from the first item 1 time
    Check Log Message    ${tc.kws[1].msgs[0]}    Item found from the first item 2 times
    Check Log Message    ${tc.kws[3].msgs[0]}    Item found from the first item 0 times

Should Contain X Times With Tuple
    Check test case    ${TESTNAME}

Should Contain X With Java Array And Vector
    [Tags]    jybot
    Check test case    ${TESTNAME}

Should Contain X With Invalid Item
    Check test case    ${TESTNAME}

Should Contain X Times With Invalid Count
    Check test case    ${TESTNAME}

Should Contain X Times Failing With Default Message
    Check test case    ${TESTNAME} 1
    Check test case    ${TESTNAME} 2
    Check test case    ${TESTNAME} 3

Should Contain X Times Failing With Defined Message
    Check test case    ${TESTNAME}

Get Count
    [Documentation]    This keyword is also tested by Should (Not) Contain X Times keywords that use this keyword internally
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Item found from the first item 2 times
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Item found from the first item 1 time
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}    Item found from the first item 1 time
    Check Log Message    ${tc.kws[3].kws[0].msgs[0]}    Item found from the first item 50 times
    Check Log Message    ${tc.kws[4].kws[0].msgs[0]}    Item found from the first item 0 times

*** Keywords ***
Verify argument type message
    [Arguments]    ${msg}    ${type1}    ${type2}
    ${type1} =    Str Type to Unicode On IronPython    ${type1}
    ${type2} =    Str Type to Unicode On IronPython    ${type2}
    Check log message    ${msg}    Argument types are:\n<type '${type1}'>\n<type '${type2}'>    DEBUG

Str Type to Unicode On IronPython
    [Arguments]    ${type}
    ${type} =    Set Variable If    "${IRONPYTHON}" and "${type}" == "str"    unicode    ${type}
    [Return]    ${type}
