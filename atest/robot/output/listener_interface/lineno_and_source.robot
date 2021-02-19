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
    START    No Operation                    6    NOT SET
    END      No Operation                    6    PASS

User keyword
    START    User Keyword                    9    NOT SET
    START    No Operation                   65    NOT SET
    END      No Operation                   65    PASS
    END      User Keyword                    9    PASS

User keyword in resource
    START    User Keyword In Resource       12    NOT SET
    START    No Operation                    3    NOT SET    source=${RESOURCE FILE}
    END      No Operation                    3    PASS       source=${RESOURCE FILE}
    END      User Keyword In Resource       12    PASS

Not run keyword
    START    Fail                           16    NOT SET
    END      Fail                           16    FAIL
    START    Fail                           17    NOT RUN
    END      Fail                           17    NOT RUN
    START    Non-existing                   18    NOT RUN
    END      Non-existing                   18    NOT RUN

FOR
    START    \${x} IN [ first | second ]    21    NOT SET    type=FOR
    START    \${x} = first                  21    NOT SET    type=FOR ITERATION
    START    No Operation                   22    NOT SET
    END      No Operation                   22    PASS
    END      \${x} = first                  21    PASS       type=FOR ITERATION
    START    \${x} = second                 21    NOT SET    type=FOR ITERATION
    START    No Operation                   22    NOT SET
    END      No Operation                   22    PASS
    END      \${x} = second                 21    PASS       type=FOR ITERATION
    END      \${x} IN [ first | second ]    21    PASS       type=FOR

FOR in keyword
    START    FOR In Keyword                 26    NOT SET
    START    \${x} IN [ once ]              68    NOT SET    type=FOR
    START    \${x} = once                   68    NOT SET    type=FOR ITERATION
    START    No Operation                   69    NOT SET
    END      No Operation                   69    PASS
    END      \${x} = once                   68    PASS       type=FOR ITERATION
    END      \${x} IN [ once ]              68    PASS       type=FOR
    END      FOR In Keyword                 26    PASS

FOR in IF
    START    True                           29    NOT SET    type=IF
    START    \${x} | \${y} IN [ x | y ]     30    NOT SET    type=FOR
    START    \${x} = x, \${y} = y           30    NOT SET    type=FOR ITERATION
    START    No Operation                   31    NOT SET
    END      No Operation                   31    PASS
    END      \${x} = x, \${y} = y           30    PASS       type=FOR ITERATION
    END      \${x} | \${y} IN [ x | y ]     30    PASS       type=FOR
    END      True                           29    PASS       type=IF

FOR in resource
    START    FOR In Resource       36    NOT SET
    START    \${x} IN [ once ]      6    NOT SET    source=${RESOURCE FILE}    type=FOR
    START    \${x} = once           6    NOT SET    source=${RESOURCE FILE}    type=FOR ITERATION
    START    Log                    7    NOT SET    source=${RESOURCE FILE}
    END      Log                    7    PASS       source=${RESOURCE FILE}
    END      \${x} = once           6    PASS       source=${RESOURCE FILE}    type=FOR ITERATION
    END      \${x} IN [ once ]      6    PASS       source=${RESOURCE FILE}    type=FOR
    END      FOR In Resource       36    PASS

IF
    START    1 > 2                 39    NOT RUN    type=IF
    START    Fail                  40    NOT RUN
    END      Fail                  40    NOT RUN
    END      1 > 2                 39    NOT RUN    type=IF
    START    1 < 2                 41    NOT SET    type=ELSE IF
    START    No Operation          42    NOT SET
    END      No Operation          42    PASS
    END      1 < 2                 41    PASS       type=ELSE IF
    START    ${EMPTY}              43    NOT RUN    type=ELSE
    START    Fail                  44    NOT RUN
    END      Fail                  44    NOT RUN
    END      ${EMPTY}              43    NOT RUN    type=ELSE

IF in keyword
    START    IF In Keyword         48    NOT SET
    START    True                  73    NOT SET    type=IF
    START    No Operation          74    NOT SET
    END      No Operation          74    PASS
    END      True                  73    PASS       type=IF
    END      IF In Keyword         48    PASS

IF in FOR
    START    \${x} IN [ 1 | 2 ]    52    NOT SET    type=FOR
    START    \${x} = 1             52    NOT SET    type=FOR ITERATION
    START    \${x} == 1            53    NOT SET    type=IF
    START    Log                   54    NOT SET
    END      Log                   54    PASS
    END      \${x} == 1            53    PASS       type=IF
    START    ${EMPTY}              55    NOT RUN    type=ELSE
    START    Fail                  56    NOT RUN
    END      Fail                  56    NOT RUN
    END      ${EMPTY}              55    NOT RUN    type=ELSE
    END      \${x} = 1             52    PASS       type=FOR ITERATION
    START    \${x} = 2             52    NOT SET    type=FOR ITERATION
    START    \${x} == 1            53    NOT RUN    type=IF
    START    Log                   54    NOT RUN
    END      Log                   54    NOT RUN
    END      \${x} == 1            53    NOT RUN    type=IF
    START    ${EMPTY}              55    NOT SET    type=ELSE
    START    Fail                  56    NOT SET
    END      Fail                  56    FAIL
    END      ${EMPTY}              55    FAIL       type=ELSE
    END      \${x} = 2             52    FAIL       type=FOR ITERATION
    END      \${x} IN [ 1 | 2 ]    52    FAIL       type=FOR

IF in resource
    START    IF In Resource        61    NOT SET
    START    True                  11    NOT SET    source=${RESOURCE FILE}    type=IF
    START    No Operation          12    NOT SET    source=${RESOURCE FILE}
    END      No Operation          12    PASS       source=${RESOURCE FILE}
    END      True                  11    PASS       source=${RESOURCE FILE}    type=IF
    END      IF In Resource        61    PASS

Test
    [Template]    Expect test
    Keyword                      5
    User keyword                 8
    User keyword in resource    11
    Not run keyword             14    FAIL
    \FOR                        20
    FOR in keyword              25
    FOR in IF                   28
    FOR in resource             35
    \IF                         38
    IF in keyword               47
    IF in FOR                   50    FAIL
    IF in resource              60
    [Teardown]    Validate tests

Suite
    START    Lineno And Source    type=SUITE
    END      Lineno And Source    type=SUITE    status=FAIL
    [Teardown]    Validate suite

*** Keywords ***
Expect
    [Arguments]    ${event}    ${name}    ${lineno}=-1    ${status}=    ${source}=${TEST CASE FILE}    ${type}=KEYWORD
    ${source} =    Normalize Path    ${source}
    ${status} =    Set Variable IF    "${status}"    \t${status}    ${EMPTY}
    Set test variable    @EXPECTED    @{EXPECTED}    ${event}\t${type}\t${name}\t${lineno}\t${source}${status}

Validate keywords
    Check Test Case    ${TESTNAME}
    Check Listener File    ${TEST NAME}.txt    @{EXPECTED}

Expect test
    [Arguments]    ${name}    ${lineno}    ${status}=PASS
    Expect    START    ${name}    ${lineno}    type=TEST
    Expect    END      ${name}    ${lineno}    ${status}    type=TEST

Validate tests
    Check Listener File    LinenoAndSourceTests.txt    @{EXPECTED}

Validate suite
    Check Listener File    LinenoAndSourceSuite.txt    @{EXPECTED}
