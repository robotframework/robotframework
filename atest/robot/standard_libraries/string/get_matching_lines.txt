*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/get_matching_lines.txt
Force Tags        pybot    jybot    regression
Resource          atest_resource.txt

*** Test Cases ***
Get Lines Containing String When Input Is Empty
    ${tc} =    Check Test Case    Get Lines Containing String When Input Is Empty
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    0 out of 0 lines matched

Get Lines Containing String When Pattern Is Empty
    ${tc} =    Check Test Case    Get Lines Containing String When Pattern Is Empty
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    5 out of 5 lines matched

Get Lines Containing String Matching One Line
    ${tc} =    Check Test Case    Get Lines Containing String Matching One Line
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched

Get Lines Containing String Matching Some Lines
    ${tc} =    Check Test Case    Get Lines Containing String Matching Some Lines
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    2 out of 5 lines matched

Get Lines Containing String With Case-Insensitive
    ${tc} =    Check Test Case    Get Lines Containing String With Case-Insensitive
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    3 out of 5 lines matched

Get Lines Matching Pattern When Input Is Empty
    ${tc} =    Check Test Case    Get Lines Matching Pattern When Input Is Empty
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    0 out of 0 lines matched

Get Lines Matching Pattern When Pattern Is Empty
    ${tc} =    Check Test Case    Get Lines Matching Pattern When Pattern Is Empty
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched

Get Lines Matching Pattern Matching One Line
    ${tc} =    Check Test Case    Get Lines Matching Pattern Matching One Line
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched

Get Lines Matching Pattern Matching Some Lines
    ${tc} =    Check Test Case    Get Lines Matching Pattern Matching Some Lines
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    2 out of 5 lines matched

Get Lines Matching Pattern With Case-Insensitive
    ${tc} =    Check Test Case    Get Lines Matching Pattern With Case-Insensitive
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    3 out of 5 lines matched

Get Lines Matching Regexp When Input Is Empty
    ${tc} =    Check Test Case    Get Lines Matching Regexp When Input Is Empty
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    0 out of 0 lines matched

Get Lines Matching Regexp When Pattern Is Empty
    ${tc} =    Check Test Case    Get Lines Matching Regexp When Pattern Is Empty
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched

Get Lines Matching Regexp Matching One Line
    ${tc} =    Check Test Case    Get Lines Matching Regexp Matching One Line
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    1 out of 5 lines matched

Get Lines Matching Regexp Matching Some Lines
    ${tc} =    Check Test Case    Get Lines Matching Regexp Matching Some Lines
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    2 out of 5 lines matched

Get Lines Matching Regexp With Case-Insensitive
    ${tc} =    Check Test Case    Get Lines Matching Regexp With Case-Insensitive
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    3 out of 5 lines matched

