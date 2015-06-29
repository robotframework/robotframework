*** Settings ***
Library           String

*** Variables ***
${INPUT}          Line 1\nLine 2\nThird line\n\nOne more row here

*** Test Cases ***
Get Lines Containing String When Input Is Empty
    Test Get Lines Containing String    ${EMPTY}    whatever    ${EMPTY}

Get Lines Containing String When Pattern Is Empty
    Test Get Lines Containing String    ${INPUT}    ${EMPTY}    ${INPUT}

Get Lines Containing String Matching One Line
    Test Get Lines Containing String    ${INPUT}    Third line    Third line

Get Lines Containing String Matching Some Lines
    Test Get Lines Containing String    ${INPUT}    Line    Line 1\nLine 2

Get Lines Containing String With Case-Insensitive
    Test Get Lines Containing String    ${INPUT}    Line    Line 1\nLine 2\nThird line    case-insensitive
    Test Get Lines Containing String    ${INPUT}    ROW    One more row here    whatever
    Test Get Lines Containing String    ${INPUT}    ROW    ${EMPTY}    ${EMPTY}

Get Lines Matching Pattern When Input Is Empty
    Test Get Lines Matching Pattern    ${EMPTY}    what*ever    ${EMPTY}

Get Lines Matching Pattern When Pattern Is Empty
    Test Get Lines Matching Pattern    ${INPUT}    ${EMPTY}    ${EMPTY}

Get Lines Matching Pattern Matching One Line
    Test Get Lines Matching Pattern    ${INPUT}    Third*    Third line
    Test Get Lines Matching Pattern    ${INPUT}    ???? 1    Line 1

Get Lines Matching Pattern Matching Some Lines
    Test Get Lines Matching Pattern    ${INPUT}    Line ?    Line 1\nLine 2
    Test Get Lines Matching Pattern    ${INPUT}    ?in*    Line 1\nLine 2
    Test Get Lines Matching Pattern    ${INPUT}    *    ${INPUT}
    Test Get Lines Matching Pattern    ${INPUT}    ??????    Line 1\nLine 2

Get Lines Matching Pattern With Case-Insensitive
    Test Get Lines Matching Pattern    ${INPUT}    *line*    Line 1\nLine 2\nThird line    case-insensitive
    Test Get Lines Matching Pattern    ${INPUT}    *LINE    Third line    whatever
    Test Get Lines Matching Pattern    ${INPUT}    *LINE*    ${EMPTY}    ${EMPTY}

Get Lines Matching Regexp When Input Is Empty
    Test Get Lines Matching Regexp    ${EMPTY}    what.*ever    ${EMPTY}

Get Lines Matching Regexp When Pattern Is Empty
    Test Get Lines Matching Regexp    ${INPUT}    ${EMPTY}    ${EMPTY}

Get Lines Matching Regexp Matching One Line
    Test Get Lines Matching Regexp    ${INPUT}    Third.*    Third line
    Test Get Lines Matching Regexp    ${INPUT}    [LMNOPQ]in. 1+    Line 1

Get Lines Matching Regexp Matching Some Lines
    Test Get Lines Matching Regexp    ${INPUT}    .* \\d    Line 1\nLine 2
    Test Get Lines Matching Regexp    ${INPUT}    (Line|Wine) [1-9]    Line 1\nLine 2
    Test Get Lines Matching Regexp    ${INPUT}    .*    ${INPUT}
    Test Get Lines Matching Regexp    ${INPUT}    .{6}    Line 1\nLine 2

Get Lines Matching Regexp With Case-Insensitive
    Test Get Lines Matching Regexp    ${INPUT}    (?i).*line.*    Line 1\nLine 2\nThird line
    Test Get Lines Matching Regexp    ${INPUT}    (?i).*LINE    Third line
    Test Get Lines Matching Regexp    ${INPUT}    .*LINE.*    ${EMPTY}

*** Keywords ***
Test Get Lines Containing String
    [Arguments]    ${input}    ${pattern}    ${expected}    ${case-insensitive}=false
    ${actual} =    Get Lines Containing String    ${input}    ${pattern}    ${case-insensitive}
    Should Be Equal    ${actual}    ${expected}

Test Get Lines Matching Pattern
    [Arguments]    ${input}    ${pattern}    ${expected}    ${case-insensitive}=no
    ${actual} =    Get Lines Matching Pattern    ${input}    ${pattern}    ${case-insensitive}
    Should Be Equal    ${actual}    ${expected}

Test Get Lines Matching Regexp
    [Arguments]    ${input}    ${pattern}    ${expected}
    ${actual} =    Get Lines Matching Regexp    ${input}    ${pattern}
    Should Be Equal    ${actual}    ${expected}
