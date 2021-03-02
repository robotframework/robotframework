*** Settings ***
Documentation   Tests for using libraries implemented with Java. This stuff is tested also in keywords/java_arguments.robot and these files should be combined.
Suite Setup     Run Tests  ${EMPTY}  test_libraries/java_libraries.robot
Force Tags      require-jython
Resource        atest_resource.robot

*** Test Cases ***
String Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  Hello world

Char Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  x
    Check Log Message  ${tc.kws[1].msgs[0]}  y

Boolean Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  Oh Yes!!
    Check Log Message  ${tc.kws[1].msgs[0]}  Oh No!!

Double Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  3.14
    Check Log Message  ${tc.kws[1].msgs[0]}  1000.0

Float Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  -3.14
    Check Log Message  ${tc.kws[1].msgs[0]}  -0.1

Long Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  1000000000000000
    Check Log Message  ${tc.kws[1].msgs[0]}  -1

Integer Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  42
    Check Log Message  ${tc.kws[1].msgs[0]}  -1

Short Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  2006
    Check Log Message  ${tc.kws[1].msgs[0]}  -100

Byte Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  8
    Check Log Message  ${tc.kws[1].msgs[0]}  0

String Array Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  Hello\nmy\nworld
    Check Log Message  ${tc.kws[1].msgs[0]}  Hi your tellus
    Should Be Empty  ${tc.kws[2].msgs}
    Check Log Message  ${tc.kws[4].msgs[0]}  Moi\nmaailma
    Check Log Message  ${tc.kws[6].msgs[0]}  a\nb\nc

Integer Array Arg
    ${tc} =  Check Test Case  ${TEST NAME}
    Check Log Message  ${tc.kws[0].msgs[0]}  1\n2\n3
    Check Log Message  ${tc.kws[1].msgs[0]}  -2006\n2006
    Should Be Empty  ${tc.body[2].messages}
    Should Be Empty  ${tc.body[3].messages}
    Check Log Message  ${tc.kws[5].msgs[0]}  -1\n1
    Check Log Message  ${tc.kws[6].msgs[0]}  -1\n1

Return Integer
    Check Test Case  ${TEST NAME}

Return Double
    Check Test Case  ${TEST NAME}

Return Boolean
    Check Test Case  ${TEST NAME}

Return String
    Check Test Case  ${TEST NAME}

Return Null
    Check Test Case  ${TEST NAME}

Return String Array
    Check Test Case  ${TEST NAME}

Return Int Array
    Check Test Case  ${TEST NAME}

