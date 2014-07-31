*** Settings ***
Documentation   This feature has been depreaced in 2.0.4 and will be removed in 2.2. See issue 193 for more information.
Suite Setup     Run Tests  ${EMPTY}  keywords/repeating_keyword.txt
Force Tags      regression  smoke  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***
Repeat Keyword Name and Arguments
    ${test} =  Check Test Case  Repeat Doing Nothing
    Verify Deprecation Messages  ${test.kws[0].msgs[0]}  1 x
    Verify Deprecation Messages  ${test.kws[1].msgs[0]}  1000x
    Equals  ${test.kws[0].name}  1 x
    Equals  ${test.kws[1].name}  1000x
    ${test} =  Check Test Case  Repeat With Arguments Doing Nothing
    Verify Deprecation Messages  ${test.kws[0].msgs[0]}  1 x
    Equals  ${test.kws[0].name}  1 x
    Fail Unless  ${test.kws[0].args} == ('Comment', 'Nothing is done')
    Verify Deprecation Messages  ${test.kws[1].msgs[0]}  42 X
    Equals  ${test.kws[1].name}  42 X
    Fail Unless  ${test.kws[1].args} == ('Comment', 'Still', 'nothing')

Repeat Keyword Messages
    ${test} =  Check Test Case  Repeat With Messages
    Verify Deprecation Messages  ${test.kws[0].msgs[0]}  1 x
    Check Log Message  ${test.kws[0].msgs[1]}  Repeating keyword, round 1/1
    Check Log Message  ${test.kws[0].kws[0].msgs[0]}  Hello, world
    Verify Deprecation Messages  ${test.kws[1].msgs[0]}  33 x
    Check Log Message  ${test.kws[1].kws[0].msgs[0]}  Hi, tellus
    Check Log Message  ${test.kws[1].kws[2].msgs[0]}  Hi, tellus
    Check Log Message  ${test.kws[1].kws[3].msgs[0]}  Hi, tellus
    Check Log Message  ${test.kws[1].kws[32].msgs[0]}  Hi, tellus

Repeating User Keyword
    ${test} =  Check Test Case  Repeating User Keyword
    ${kws} =  Set  ${test.keywords}
    Verify Deprecation Messages  ${kws[0].msgs[0]}  1 x
    Check Log Message  ${kws[0].kws[0].kws[0].msgs[0]}  Hello from Repeating UK
    Check Log Message  ${kws[0].kws[0].kws[1].msgs[0]}  Yo, world
    Check Log Message  ${kws[1].kws[0].kws[0].msgs[0]}  Hello from Repeating UK
    Check Log Message  ${kws[1].kws[0].kws[1].msgs[0]}  Yo, tellus
    Check Log Message  ${kws[1].kws[1].kws[0].msgs[0]}  Hello from Repeating UK
    Check Log Message  ${kws[1].kws[1].kws[1].msgs[0]}  Yo, tellus
    ${kws} =  Set  ${kws[2].keywords}
    Check Log Message  ${kws[0].kws[0].kws[0].msgs[0]}  Hello from Repeating UK
    Check Log Message  ${kws[0].kws[0].kws[1].msgs[0]}  Sub kw

Repeating Inside User Keyword
    ${test} =  Check Test Case  Repeating Inside User Keyword
    Test Repeating Inside UK  ${test.kws[0].kws[0]}

Repeating Inside Repeating
    ${test} =  Check Test Case  Repeating Inside Repeating
    Test Repeating Inside UK  ${test.kws[0].kws[0].kws[0]}
    Test Repeating Inside UK  ${test.kws[0].kws[1].kws[0]}
    Test Repeating Inside UK  ${test.kws[0].kws[2].kws[0]}
    Test Repeating Inside UK  ${test.kws[0].kws[3].kws[0]}

Failing Repeat Keyword
    ${test} =  Check Test Case  Failing Repeat Keyword
    Check Log Message  ${test.kws[0].kws[0].msgs[0]}  Failing instead of repeating  FAIL
    ${test} =  Check Test Case  Not First Repeat Keyword Failing
    Check Log Message  ${test.kws[0].kws[0].kws[0].msgs[0]}  \${limit} = 9
    Check Log Message  ${test.kws[0].kws[1].kws[0].msgs[0]}  \${limit} = 8
    Check Log Message  ${test.kws[0].kws[2].kws[0].msgs[0]}  \${limit} = 7
    Check Log Message  ${test.kws[0].kws[9].kws[0].msgs[0]}  \${limit} = 0
    Check Log Message  ${test.kws[0].kws[9].kws[2].msgs[1]}  Recursion limit exceeded  FAIL
    ${test} =  Check Test Case  Failing Repeat Keyword and Teardown
    Check Log Message  ${test.kws[0].kws[0].msgs[0]}  Failing, again, instead of repeating  FAIL
    ${test} =  Check Test Case  Non-Exising Variable In Repeat Keyword
    Check Log Message  ${test.kws[0].kws[0].msgs[0]}  Resolving variable '\${non-exiting-variable}' failed: Non-existing variable '\${non}'.  FAIL

Non Existing Keyword In Repeat
    Check Test Case  Non Existing Keyword In Repeat

Zero Repeat
    [Documentation]  Zero repeat means not executing the keyword at all
    ${test} =  Check Test Case  Zero Repeat
    Equals  ${test.kws[0].name}  0 x

Negative Repeat
    [Documentation]  Negative repeat is the same as zero repeat
    ${test} =  Check Test Case  Negative Repeat
    Equals  ${test.kws[0].name}  -1 x

Repeat With Valid Int Variable
    ${test} =  Check Test Case  Repeat With Valid Int Variable
    Verify Deprecation Messages  ${test.kws[0].msgs[0]}  \${3} x
    Equals  ${test.kws[0].name}  \${3} x
    Check Log Message  ${test.kws[0].kws[0].msgs[0]}  Repeated 3 times
    Check Log Message  ${test.kws[0].kws[1].msgs[0]}  Repeated 3 times
    Check Log Message  ${test.kws[0].kws[2].msgs[0]}  Repeated 3 times
    Equals  ${test.kws[1].name}  \${2}X
    Check Log Message  ${test.kws[1].kws[0].msgs[0]}  Repeated 2 times
    Check Log Message  ${test.kws[1].kws[1].msgs[0]}  Repeated 2 times
    Equals  ${test.kws[2].name}  \${0} X

Repeat With Valid String Variable
    ${test} =  Check Test Case  Repeat With Valid String Variable
    Equals  ${test.kws[1].name}  \${foo} x
    Check Log Message  ${test.kws[1].kws[0].msgs[0]}  Repeated 4 times
    Check Log Message  ${test.kws[1].kws[1].msgs[0]}  Repeated 4 times
    Check Log Message  ${test.kws[1].kws[2].msgs[0]}  Repeated 4 times
    Check Log Message  ${test.kws[1].kws[3].msgs[0]}  Repeated 4 times

Repeat With Variable Using Different Values
    Check Test Case  Repeat With Variable Using Different Values In One test
    Check Test Case  Repeat With Variable Using Different Values In Another test

Repeat With Invalid String Variable
    Check Test Case  ${TEST_NAME}

No Repeat With Variable value 2x
    Check Test Case  No Repeat With Variable Value 2x

Repeat With Non Existing Variable Fails
    ${test} =  Check Test Case  Repeat With Non Existing Variable Fails
    Check Log Message  ${test.kws[0].messages[1]}  Non-existing variable '\${foo}'.  FAIL

Non Existing Keyword In Repeat With Variable
    Check Test Case  Non Existing Keyword In Repeat With Variable

Normal Keyword With X At The End
    Check Test Case  Normal Keyword With X At The End

*** Keywords ***
Test Repeating Inside UK
    [Arguments]  ${kw}
    Check Log Message  ${kw.kws[0].kws[0].msgs[0]}  Hello from Repeating UK
    Check Log Message  ${kw.kws[0].kws[1].msgs[0]}  Inside UK
    Check Log Message  ${kw.kws[1].kws[0].msgs[0]}  Hello from Repeating UK
    Check Log Message  ${kw.kws[1].kws[1].msgs[0]}  Inside UK
    Check Log Message  ${kw.kws[2].kws[0].msgs[0]}  Hello from Repeating UK
    Check Log Message  ${kw.kws[2].kws[1].msgs[0]}  Inside UK

Verify Deprecation Messages
    [Arguments]  ${msg}  ${x times}
    ${exp} =  Catenate  Keyword '${ x times}' is deprecated. Replace X times syntax with 'Repeat Keyword'.
    Check Log Message  ${msg}  ${exp}  WARN
    Check Syslog Contains  | WARN \ |  ${exp}

