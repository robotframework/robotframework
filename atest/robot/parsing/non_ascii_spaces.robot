*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    parsing/non_ascii_spaces.robot
Resource         atest_resource.robot

*** Test Cases ***
In suite settings
    ${tc} =    Check Test Case    In test and keywords
    Check Log Message    ${tc.setup.kws[0].msgs[0]}       ': :'
    Check Log Message    ${tc.teardown.kws[0].msgs[0]}    ': :'
    Normalization deprecated    0    Test\\xa0Setup                  2
    Normalization deprecated    1    No-break\\xa0space              2
    Normalization deprecated    2    :\\xa0:                         2
    Normalization deprecated    3    Test\\u1680Teardown             3
    Normalization deprecated    4    Ogham\\u1680space\\u1680mark    3
    Normalization deprecated    5    :\\u1680:                       3

In variables
    Normalization deprecated    6    \${NO-BREAK\\xa0SPACE}\\xa0=    6
    Normalization deprecated    7    :\\xa0:                         6
    Normalization deprecated    8    \${OGHAM\\u1680SPACE\\u1680MARK}\\u1680=    7
    Normalization deprecated    9    :\\u1680:                                   7
    Normalization deprecated    10   \${IDEOGRAPHIC\\u3000SPACE}\\u3000=         8
    Normalization deprecated    11   :\\u3000:                                   8

In test and keywords
    ${tc} =    Check Test Case    ${TESTNAME}
    Normalization deprecated    12    [\\xa0Tags\\u1680]                  14
    Normalization deprecated    13    NBSP\\xa0and\\u1680Ogham            14
    Normalization deprecated    14    \${x}\\xa0=                         15
    Normalization deprecated    15    No-break\\xa0space                  15
    Normalization deprecated    16    :\\xa0:                             15
    Normalization deprecated    17    \${x}\\u1680=                       16
    Normalization deprecated    18    Ogham\\u1680space\\u1680mark        16
    Normalization deprecated    19    :\\u1680:                           16
    Normalization deprecated    20    \${x}\\u3000=                       17
    Normalization deprecated    21    Ideographic\\u3000space             17
    Normalization deprecated    22    :\\u3000:                           17
    Normalization deprecated    23    No-break\\xa0space                  21
    Normalization deprecated    24    :\\xa0:                             21
    Normalization deprecated    25    No-break\\xa0space                  25
    Normalization deprecated    26    :\\xa0:                             25
    Normalization deprecated    27    No-break\\xa0space                  28
    Normalization deprecated    28    [\\xa0Arguments\\xa0]               29
    Normalization deprecated    29    Should\\xa0be\\xa0equal             31
    Normalization deprecated    30    Should\\xa0be\\xa0equal             32
    Normalization deprecated    31    Should\\xa0be\\xa0equal             33
    Normalization deprecated    32    \${NO-BREAK\\xa0SPACE}              33
    Normalization deprecated    33    Ogham\\u1680space\\u1680mark        35
    Normalization deprecated    34    [\\u1680Arguments\\u1680]           36
    Normalization deprecated    35    Should\\u1680be\\u1680equal         38
    Normalization deprecated    36    Should\\u1680be\\u1680equal         39
    Normalization deprecated    37    Should\\u1680be\\u1680equal         40
    Normalization deprecated    38    \${OGHAM\\u1680SPACE\\u1680MARK}    40
    Normalization deprecated    39    Ideographic\\u3000space             42
    Normalization deprecated    40    [\\u3000Arguments\\u3000]           43
    Normalization deprecated    41    Should\\u3000be\\u3000equal         45
    Normalization deprecated    42    Should\\u3000be\\u3000equal         46
    Normalization deprecated    43    Should\\u3000be\\u3000equal         47
    Normalization deprecated    44    \${IDEOGRAPHIC\\u3000SPACE}         47

As separator
    Check Test Case    ${TESTNAME}

With pipes
    Check Test Case    ${TESTNAME}

In header
    Check Test Case    ${TESTNAME}
    Normalization deprecated    45    ***\\xa0Test\\u1680Cases\\u3000***    49

*** Keywords ***
Normalization deprecated
    [Arguments]    ${index}    ${text}    ${line}
    ${path} =    Normalize Path    ${DATADIR}/parsing/non_ascii_spaces.robot
    ${msg} =    Catenate
    ...    Converting whitespace characters to ASCII spaces during parsing is deprecated.
    ...    Fix '${text}' in file '${path}' on line ${line}.
    Check Log Message    ${ERRORS}[${index}]    ${msg}    WARN
