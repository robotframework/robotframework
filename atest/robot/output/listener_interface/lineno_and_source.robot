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
    START    KEYWORD          No Operation                    6    NOT SET
    END      KEYWORD          No Operation                    6    PASS

User keyword
    START    KEYWORD          User Keyword                    9    NOT SET
    START    KEYWORD          No Operation                   65    NOT SET
    END      KEYWORD          No Operation                   65    PASS
    START    RETURN           ${EMPTY}                       66    NOT SET
    END      RETURN           ${EMPTY}                       66    PASS
    END      KEYWORD          User Keyword                    9    PASS

User keyword in resource
    START    KEYWORD          User Keyword In Resource       12    NOT SET
    START    KEYWORD          No Operation                    3    NOT SET    source=${RESOURCE FILE}
    END      KEYWORD          No Operation                    3    PASS       source=${RESOURCE FILE}
    END      KEYWORD          User Keyword In Resource       12    PASS

Not run keyword
    START    KEYWORD          Fail                           16    NOT SET
    END      KEYWORD          Fail                           16    FAIL
    START    KEYWORD          Fail                           17    NOT RUN
    END      KEYWORD          Fail                           17    NOT RUN
    START    KEYWORD          Non-existing                   18    NOT RUN
    END      KEYWORD          Non-existing                   18    NOT RUN

FOR
    START    FOR              \${x} IN [ first | second ]    21    NOT SET
    START    FOR ITERATION    \${x} = first                  21    NOT SET
    START    KEYWORD          No Operation                   22    NOT SET
    END      KEYWORD          No Operation                   22    PASS
    END      FOR ITERATION    \${x} = first                  21    PASS
    START    FOR ITERATION    \${x} = second                 21    NOT SET
    START    KEYWORD          No Operation                   22    NOT SET
    END      KEYWORD          No Operation                   22    PASS
    END      FOR ITERATION    \${x} = second                 21    PASS
    END      FOR              \${x} IN [ first | second ]    21    PASS

FOR in keyword
    START    KEYWORD          FOR In Keyword                 26    NOT SET
    START    FOR              \${x} IN [ once ]              69    NOT SET
    START    FOR ITERATION    \${x} = once                   69    NOT SET
    START    KEYWORD          No Operation                   70    NOT SET
    END      KEYWORD          No Operation                   70    PASS
    END      FOR ITERATION    \${x} = once                   69    PASS
    END      FOR              \${x} IN [ once ]              69    PASS
    END      KEYWORD          FOR In Keyword                 26    PASS

FOR in IF
    START    IF               True                           29    NOT SET
    START    FOR              \${x} | \${y} IN [ x | y ]     30    NOT SET
    START    FOR ITERATION    \${x} = x, \${y} = y           30    NOT SET
    START    KEYWORD          No Operation                   31    NOT SET
    END      KEYWORD          No Operation                   31    PASS
    END      FOR ITERATION    \${x} = x, \${y} = y           30    PASS
    END      FOR              \${x} | \${y} IN [ x | y ]     30    PASS
    END      IF               True                           29    PASS

FOR in resource
    START    KEYWORD          FOR In Resource                36    NOT SET
    START    FOR              \${x} IN [ once ]               6    NOT SET    source=${RESOURCE FILE}
    START    FOR ITERATION    \${x} = once                    6    NOT SET    source=${RESOURCE FILE}
    START    KEYWORD          Log                             7    NOT SET    source=${RESOURCE FILE}
    END      KEYWORD          Log                             7    PASS       source=${RESOURCE FILE}
    END      FOR ITERATION    \${x} = once                    6    PASS       source=${RESOURCE FILE}
    END      FOR              \${x} IN [ once ]               6    PASS       source=${RESOURCE FILE}
    END      KEYWORD          FOR In Resource                36    PASS

IF
    START   IF                1 > 2                          39    NOT RUN
    START   KEYWORD           Fail                           40    NOT RUN
    END     KEYWORD           Fail                           40    NOT RUN
    END     IF                1 > 2                          39    NOT RUN
    START   ELSE IF           1 < 2                          41    NOT SET
    START   KEYWORD           No Operation                   42    NOT SET
    END     KEYWORD           No Operation                   42    PASS
    END     ELSE IF           1 < 2                          41    PASS
    START   ELSE              ${EMPTY}                       43    NOT RUN
    START   KEYWORD           Fail                           44    NOT RUN
    END     KEYWORD           Fail                           44    NOT RUN
    END     ELSE              ${EMPTY}                       43    NOT RUN

IF in keyword
    START   KEYWORD           IF In Keyword                  48    NOT SET
    START   IF                True                           74    NOT SET
    START   KEYWORD           No Operation                   75    NOT SET
    END     KEYWORD           No Operation                   75    PASS
    START   RETURN            ${EMPTY}                       76    NOT SET
    END     RETURN            ${EMPTY}                       76    PASS
    END     IF                True                           74    PASS
    END     KEYWORD           IF In Keyword                  48    PASS

IF in FOR
    START   FOR               \${x} IN [ 1 | 2 ]             52    NOT SET
    START   FOR ITERATION     \${x} = 1                      52    NOT SET
    START   IF                \${x} == 1                     53    NOT SET
    START   KEYWORD           Log                            54    NOT SET
    END     KEYWORD           Log                            54    PASS
    END     IF                \${x} == 1                     53    PASS
    START   ELSE              ${EMPTY}                       55    NOT RUN
    START   KEYWORD           Fail                           56    NOT RUN
    END     KEYWORD           Fail                           56    NOT RUN
    END     ELSE              ${EMPTY}                       55    NOT RUN
    END     FOR ITERATION     \${x} = 1                      52    PASS
    START   FOR ITERATION     \${x} = 2                      52    NOT SET
    START   IF                \${x} == 1                     53    NOT RUN
    START   KEYWORD           Log                            54    NOT RUN
    END     KEYWORD           Log                            54    NOT RUN
    END     IF                \${x} == 1                     53    NOT RUN
    START   ELSE              ${EMPTY}                       55    NOT SET
    START   KEYWORD           Fail                           56    NOT SET
    END     KEYWORD           Fail                           56    FAIL
    END     ELSE              ${EMPTY}                       55    FAIL
    END     FOR ITERATION     \${x} = 2                      52    FAIL
    END     FOR               \${x} IN [ 1 | 2 ]             52    FAIL

IF in resource
    START   KEYWORD           IF In Resource                 61    NOT SET
    START   IF                True                           11    NOT SET    source=${RESOURCE FILE}
    START   KEYWORD           No Operation                   12    NOT SET    source=${RESOURCE FILE}
    END     KEYWORD           No Operation                   12    PASS       source=${RESOURCE FILE}
    END     IF                True                           11    PASS       source=${RESOURCE FILE}
    END     KEYWORD           IF In Resource                 61    PASS

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
    START    SUITE    Lineno And Source
    END      SUITE    Lineno And Source    status=FAIL
    [Teardown]    Validate suite

*** Keywords ***
Expect
    [Arguments]    ${event}    ${type}    ${name}    ${lineno}=-1    ${status}=    ${source}=${TEST CASE FILE}
    ${source} =    Normalize Path    ${source}
    ${status} =    Set Variable IF    "${status}"    \t${status}    ${EMPTY}
    Set test variable    @EXPECTED    @{EXPECTED}    ${event}\t${type}\t${name}\t${lineno}\t${source}${status}

Validate keywords
    Check Test Case    ${TESTNAME}
    Check Listener File    ${TEST NAME}.txt    @{EXPECTED}

Expect test
    [Arguments]    ${name}    ${lineno}    ${status}=PASS
    Expect    START    TEST    ${name}    ${lineno}
    Expect    END      TEST    ${name}    ${lineno}    ${status}

Validate tests
    Check Listener File    LinenoAndSourceTests.txt    @{EXPECTED}

Validate suite
    Check Listener File    LinenoAndSourceSuite.txt    @{EXPECTED}
