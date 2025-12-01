*** Settings ***
Library           String

*** Variables ***
${INPUT}          Line 1\nLine 2\nThird line\n\nOne more row here

*** Test Cases ***
Get Lines Containing String When Input Is Empty
    [Template]    Test Get Lines Containing String
    ${EMPTY}    whatever    ${EMPTY}

Get Lines Containing String When Pattern Is Empty
    [Template]    Test Get Lines Containing String
    ${INPUT}    ${EMPTY}    ${INPUT}

Get Lines Containing String Matching One Line
    [Template]    Test Get Lines Containing String
    ${INPUT}    Third line    Third line
    ${INPUT}    Third line    Third line              False

Get Lines Containing String Matching Some Lines
    [Template]    Test Get Lines Containing String
    ${INPUT}    Line    Line 1\nLine 2

Get Lines Containing String With Case-Insensitive
    [Template]    Test Get Lines Containing String
    ${INPUT}                Line    Line 1\nLine 2\nThird line    case-insensitive
    ${INPUT}                ROW     One more row here             True
    ${INPUT}                ROW     ${EMPTY}                      ${EMPTY}
    Straße\n...\nHassu\n    SS      Straße\nHassu                 True

Get Lines Containing String with bytes
    [Template]    Test Get Lines Containing String
    ${{b""}}             ${{b"whatever"}}    ${EMPTY}    type=bytes
    ${{b""}}             whatever            ${EMPTY}    type=bytes
    ${{b"1\n2"}}         ${{b"1"}}           1           type=bytes
    ${{b"1\n2"}}         1                   1           type=bytes
    ${{b"A1\nB\na2"}}    ${{b"a"}}           A1\na2      type=bytes    ignore_case=True
    ${{b"A1\nB\na2"}}    A                   A1\na2      type=bytes    ignore_case=True

Get Lines Matching Pattern When Input Is Empty
    [Template]    Test Get Lines Matching Pattern
    ${EMPTY}    what*ever    ${EMPTY}

Get Lines Matching Pattern When Pattern Is Empty
    [Template]    Test Get Lines Matching Pattern
    ${INPUT}    ${EMPTY}    ${EMPTY}

Get Lines Matching Pattern Matching One Line
    [Template]    Test Get Lines Matching Pattern
    ${INPUT}    Third*    Third line
    ${INPUT}    ???? 1    Line 1                       False

Get Lines Matching Pattern Matching Some Lines
    [Template]    Test Get Lines Matching Pattern
    ${INPUT}    Line ?    Line 1\nLine 2
    ${INPUT}    ?in*      Line 1\nLine 2
    ${INPUT}    *         ${INPUT}
    ${INPUT}    ??????    Line 1\nLine 2

Get Lines Matching Pattern With Case-Insensitive
    [Template]    Test Get Lines Matching Pattern
    ${INPUT}                *line*    Line 1\nLine 2\nThird line    case-insensitive
    ${INPUT}                *LINE     Third line                    True
    ${INPUT}                *LINE*    ${EMPTY}                      ${EMPTY}
    Straße\n...\nHassu\n    *SS?      Straße\nHassu                 True

Get Lines Matching Pattern with bytes
    [Template]    Test Get Lines Matching Pattern
    ${{b""}}             ${{b"whatever"}}    ${EMPTY}    type=bytes
    ${{b""}}             whatever            ${EMPTY}    type=bytes
    ${{b"1\n2"}}         ${{b"1"}}           1           type=bytes
    ${{b"1\n2"}}         1                   1           type=bytes
    ${{b"A1\nB\na2"}}    ${{b"a?"}}          A1\na2      type=bytes    ignore_case=True
    ${{b"A1\nB\na2"}}    A[1-2]              A1\na2      type=bytes    ignore_case=True

Get Lines Matching Regexp When Input Is Empty
    [Template]    Test Get Lines Matching Regexp
    ${EMPTY}    what.*ever    ${EMPTY}

Get Lines Matching Regexp When Pattern Is Empty
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}    ${EMPTY}    ${EMPTY}
    3 empty\n\n\n\n    ${EMPTY}    \n\n

Get Lines Matching Regexp Requires Exact Match By Default
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}    more|row    ${EMPTY}

Get Lines Matching Regexp Matching One Line
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}    Third.*           Third line
    ${INPUT}    [LMNOPQ]in. 1+    Line 1

Get Lines Matching Regexp Matching Some Lines
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}    .* \\d               Line 1\nLine 2
    ${INPUT}    (Line|Wine) [1-9]    Line 1\nLine 2
    ${INPUT}    .*                   ${INPUT}
    ${INPUT}    .{6}                 Line 1\nLine 2

Get Lines Matching Regexp With Case-Insensitive
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}    (?i).*line.*    Line 1\nLine 2\nThird line
    ${INPUT}    .*line.*        Line 1\nLine 2\nThird line    flags=IGNORECASE
    ${INPUT}    (?i).*LINE      Third line
    ${INPUT}    .*LINE.*        ${EMPTY}

Get Lines Matching Regexp With Partial Match
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}    more|row    One more row here    partial_match=True

Get Lines Matching Regexp With Partial Match Matching One Line
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}    One     One more row here    partial_match=True
    ${INPUT}    here    One more row here    partial_match=True
    ${INPUT}    1       Line 1               partial_match=True

Get Lines Matching Regexp With Partial Match Matching Some Lines
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}    .* \\d    Line 1\nLine 2                   partial_match=True
    ${INPUT}    (Line|Wine) [1-9]    Line 1\nLine 2        partial_match=True
    ${INPUT}    1|2       Line 1\nLine 2                   partial_match=True
    ${INPUT}    ^.*e$     Third line\nOne more row here    partial_match=True
    ${INPUT}    .{6}      Line 1\nLine 2\nThird line\nOne more row here    partial_match=True
    ${INPUT}    .*        ${INPUT}                         partial_match=True

Get Lines Matching Regexp With Partial Match And Case-Insensitive
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}    (?i)line    Line 1\nLine 2\nThird line    partial_match=True
    ${INPUT}    (?i)LINE    Line 1\nLine 2\nThird line    partial_match=True
    ${INPUT}    LINE        ${EMPTY}                      partial_match=True

Get Lines Matching Regexp With Partial Match When Pattern Is Empty
    [Template]    Test Get Lines Matching Regexp
    ${INPUT}           ${EMPTY}    ${INPUT}         partial_match=True
    3 empty\n\n\n\n    ${EMPTY}    3 empty\n\n\n    partial_match=True

Get Lines Matching Regexp with bytes
    [Template]    Test Get Lines Matching Regexp
    ${{b""}}             ${{b"whatever"}}    ${EMPTY}    type=bytes
    ${{b""}}             whatever            ${EMPTY}    type=bytes
    ${{b"1\n2"}}         ${{b"1"}}           1           type=bytes
    ${{b"1\n2"}}         1                   1           type=bytes
    ${{b"A1\nB\na2"}}    ${{b"a."}}          A1\na2      type=bytes    flags=IGNORECASE
    ${{b"A1\nB\na2"}}    A[1-2]              A1\na2      type=bytes    flags=I | S

*** Keywords ***
Test Get Lines Containing String
    [Arguments]    ${input}    ${pattern}    ${expected}    ${ignore_case}=False    ${type}=str
    ${actual} =    Get Lines Containing String    ${input}    ${pattern}    ${ignore_case}
    Should Be Equal    ${actual}    ${expected}    type=${type}
    ${actual} =    Get Lines Containing String    ${input}    ${pattern}    ignore_case=${ignore_case}
    Should Be Equal    ${actual}    ${expected}    type=${type}

Test Get Lines Matching Pattern
    [Arguments]    ${input}    ${pattern}    ${expected}    ${ignore_case}=False    ${type}=str
    ${actual} =    Get Lines Matching Pattern    ${input}    ${pattern}    ${ignore_case}
    Should Be Equal    ${actual}    ${expected}    type=${type}
    ${actual} =    Get Lines Matching Pattern    ${input}    ${pattern}    ignore_case=${ignore_case}
    Should Be Equal    ${actual}    ${expected}    type=${type}

Test Get Lines Matching Regexp
    [Arguments]    ${input}    ${pattern}    ${expected}    ${type}=str    &{config}
    ${actual} =    Get Lines Matching Regexp    ${input}    ${pattern}    &{config}
    Should Be Equal    ${actual}    ${expected}    type=${type}
