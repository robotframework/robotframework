*** Settings ***
Suite Setup          Run Tests    --listener ${LISTENER DIR}/LinenoAndSource.py    ${TEST CASE FILE}
Test Template        Expect
Test Teardown        Validate keywords
Resource             listener_resource.robot

*** Variables ***
${TEST CASE FILE}    ${LISTENER DIR}/lineno_and_source.robot
${RESOURCE FILE}     ${LISTENER DIR}/lineno_and_source.resource
@{EXPECTED}

*** Test Cases ***
Keyword
    START    No Operation                    7
    END      No Operation                    7

User keyword
    START    User Keyword                   10
    START    No Operation                   66
    END      No Operation                   66
    END      User Keyword                   10

User keyword in resource
    START    User Keyword In Resource       13
    START    No Operation                    3    source=${RESOURCE FILE}
    END      No Operation                    3    source=${RESOURCE FILE}
    END      User Keyword In Resource       13

Not run keyword
    START    Fail                           17
    END      Fail                           17
    START    Fail                           18
    END      Fail                           18    run=False
    START    Non-existing                   19
    END      Non-existing                   19    run=False

FOR
    START    \${x} IN [ first | second ]    22    type=FOR
    START    \${x} = first                  22    type=FOR ITERATION
    START    No Operation                   23
    END      No Operation                   23
    END      \${x} = first                  22    type=FOR ITERATION
    START    \${x} = second                 22    type=FOR ITERATION
    START    No Operation                   23
    END      No Operation                   23
    END      \${x} = second                 22    type=FOR ITERATION
    END      \${x} IN [ first | second ]    22    type=FOR

FOR in keyword
    START    FOR In Keyword                 27
    START    \${x} IN [ once ]              69    type=FOR
    START    \${x} = once                   69    type=FOR ITERATION
    START    No Operation                   70
    END      No Operation                   70
    END      \${x} = once                   69    type=FOR ITERATION
    END      \${x} IN [ once ]              69    type=FOR
    END      FOR In Keyword                 27

FOR in IF
    START    True                           30    type=IF
    START    \${x} | \${y} IN [ x | y ]     31    type=FOR
    START    \${x} = x, \${y} = y           31    type=FOR ITERATION
    START    No Operation                   32
    END      No Operation                   32
    END      \${x} = x, \${y} = y           31    type=FOR ITERATION
    END      \${x} | \${y} IN [ x | y ]     31    type=FOR
    END      True                           30    type=IF

FOR in resource
    START    FOR In Resource                37
    START    \${x} IN [ once ]               6    source=${RESOURCE FILE}    type=FOR
    START    \${x} = once                    6    source=${RESOURCE FILE}    type=FOR ITERATION
    START    Log                             7    source=${RESOURCE FILE}
    END      Log                             7    source=${RESOURCE FILE}
    END      \${x} = once                    6    source=${RESOURCE FILE}    type=FOR ITERATION
    END      \${x} IN [ once ]               6    source=${RESOURCE FILE}    type=FOR
    END      FOR In Resource                37

IF
    START    1 > 2                          40    type=IF
    START    Fail                           41
    END      Fail                           41    run=False
    END      1 > 2                          40    run=False    type=IF
    START    1 < 2                          42    type=ELSE IF
    START    No Operation                   43
    END      No Operation                   43
    END      1 < 2                          42    type=ELSE IF
    START    ${EMPTY}                       44    type=ELSE
    START    Fail                           45
    END      Fail                           45    run=False
    END      ${EMPTY}                       44    type=ELSE    run=False

IF in keyword
    START    IF In Keyword                  49
    START    True                           74    type=IF
    START    No Operation                   75
    END      No Operation                   75
    END      True                           74    type=IF
    END      IF In Keyword                  49

IF in FOR
    START    \${x} IN [ 1 | 2 ]             53    type=FOR
    START    \${x} = 1                      53    type=FOR ITERATION
    START    \${x} == 1                     54    type=IF
    START    Log                            55
    END      Log                            55
    END      \${x} == 1                     54    type=IF
    START    ${EMPTY}                       56    type=ELSE
    START    Fail                           57
    END      Fail                           57    run=False
    END      ${EMPTY}                       56    type=ELSE    run=False
    END      \${x} = 1                      53    type=FOR ITERATION
    START    \${x} = 2                      53    type=FOR ITERATION
    START    \${x} == 1                     54    type=IF
    START    Log                            55
    END      Log                            55    run=False
    END      \${x} == 1                     54    type=IF    run=False
    START    ${EMPTY}                       56    type=ELSE
    START    Fail                           57
    END      Fail                           57
    END      ${EMPTY}                       56    type=ELSE
    END      \${x} = 2                      53    type=FOR ITERATION
    END      \${x} IN [ 1 | 2 ]             53    type=FOR

IF in resource
    START    IF In Resource                 62
    START    True                           11    source=${RESOURCE FILE}    type=IF
    START    No Operation                   12    source=${RESOURCE FILE}
    END      No Operation                   12    source=${RESOURCE FILE}
    END      True                           11    source=${RESOURCE FILE}    type=IF
    END      IF In Resource                 62

Test
    [Template]    Expect test
    Keyword                      6
    User keyword                 9
    User keyword in resource    12
    Not run keyword             15
    \FOR                        21
    FOR in keyword              26
    FOR in IF                   29
    FOR in resource             36
    \IF                         39
    IF in keyword               48
    IF in FOR                   51
    IF in resource              61
    [Teardown]    Validate tests

Suite
    START    Lineno And Source    type=SUITE
    END      Lineno And Source    type=SUITE
    [Teardown]    Validate suite

*** Keywords ***
Expect
    [Arguments]    ${event}    ${name}    ${lineno}=-1    ${source}=${TEST CASE FILE}    ${type}=KEYWORD    ${run}=True
    ${source} =    Normalize Path    ${source}
    ${status} =    Set Variable IF    ${run}    ${EMPTY}    \tNOT RUN
    Set test variable    @EXPECTED    @{EXPECTED}    ${event}\t${type}\t${name}\t${lineno}\t${source}${status}

Validate keywords
    Check Test Case    ${TESTNAME}
    Check Listener File    ${TEST NAME}.txt    @{EXPECTED}

Expect test
    [Arguments]    ${name}    ${lineno}
    Expect    START    ${name}    ${lineno}    type=TEST
    Expect    END      ${name}    ${lineno}    type=TEST

Validate tests
    Check Listener File    LinenoAndSourceTests.txt    @{EXPECTED}

Validate suite
    Check Listener File    LinenoAndSourceSuite.txt    @{EXPECTED}
