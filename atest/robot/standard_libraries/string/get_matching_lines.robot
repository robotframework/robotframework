*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/get_matching_lines.robot
Resource          atest_resource.robot

*** Test Cases ***
Get Lines Containing String When Input Is Empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    0 out of 0 lines matched.

Get Lines Containing String When Pattern Is Empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    5 out of 5 lines matched.

Get Lines Containing String Matching One Line
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched.

Get Lines Containing String Matching Some Lines
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    2 out of 5 lines matched.

Get Lines Containing String With Case-Insensitive
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    3 out of 5 lines matched.

Get Lines Matching Pattern When Input Is Empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    0 out of 0 lines matched.

Get Lines Matching Pattern When Pattern Is Empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched.

Get Lines Matching Pattern Matching One Line
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched.

Get Lines Matching Pattern Matching Some Lines
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    2 out of 5 lines matched.

Get Lines Matching Pattern With Case-Insensitive
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    3 out of 5 lines matched.

Get Lines Matching Regexp When Input Is Empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    0 out of 0 lines matched.

Get Lines Matching Regexp When Pattern Is Empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched.
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    3 out of 4 lines matched.

Get Lines Matching Regexp Requires Exact Match By Default
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    0 out of 5 lines matched.

Get Lines Matching Regexp Matching One Line
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched.

Get Lines Matching Regexp Matching Some Lines
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    2 out of 5 lines matched.

Get Lines Matching Regexp With Case-Insensitive
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    3 out of 5 lines matched.

Get Lines Matching Regexp With Partial Match
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched.

Get Lines Matching Regexp With Partial Match Matching One Line
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched.

Get Lines Matching Regexp With Partial Match Matching Some Lines
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    2 out of 5 lines matched.

Get Lines Matching Regexp With Partial Match And Case-Insensitive
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    3 out of 5 lines matched.

Get Lines Matching Regexp With Partial Match When Pattern Is Empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    5 out of 5 lines matched.
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    4 out of 4 lines matched.
