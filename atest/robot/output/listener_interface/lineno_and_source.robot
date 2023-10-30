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
    \END     KEYWORD          No Operation                    6    PASS

User keyword
    START    KEYWORD          User Keyword                    9    NOT SET
    START    KEYWORD          No Operation                  101    NOT SET
    \END     KEYWORD          No Operation                  101    PASS
    START    RETURN           ${EMPTY}                      102    NOT SET
    \END     RETURN           ${EMPTY}                      102    PASS
    \END     KEYWORD          User Keyword                    9    PASS

User keyword in resource
    START    KEYWORD          User Keyword In Resource       12    NOT SET
    START    KEYWORD          No Operation                    3    NOT SET    source=${RESOURCE FILE}
    \END     KEYWORD          No Operation                    3    PASS       source=${RESOURCE FILE}
    \END     KEYWORD          User Keyword In Resource       12    PASS

Not run keyword
    START    KEYWORD          Fail                           16    NOT SET
    \END     KEYWORD          Fail                           16    FAIL
    START    KEYWORD          Fail                           17    NOT RUN
    \END     KEYWORD          Fail                           17    NOT RUN
    START    KEYWORD          Non-existing                   18    NOT RUN
    \END     KEYWORD          Non-existing                   18    NOT RUN

FOR
    START    FOR              \${x} IN first second          21    NOT SET
    START    ITERATION        \${x} = first                  21    NOT SET
    START    KEYWORD          No Operation                   22    NOT SET
    \END     KEYWORD          No Operation                   22    PASS
    \END     ITERATION        \${x} = first                  21    PASS
    START    ITERATION        \${x} = second                 21    NOT SET
    START    KEYWORD          No Operation                   22    NOT SET
    \END     KEYWORD          No Operation                   22    PASS
    \END     ITERATION        \${x} = second                 21    PASS
    \END     FOR              \${x} IN first second          21    PASS

FOR in keyword
    START    KEYWORD          FOR In Keyword                 26    NOT SET
    START    FOR              \${x} IN once                 105    NOT SET
    START    ITERATION        \${x} = once                  105    NOT SET
    START    KEYWORD          No Operation                  106    NOT SET
    \END     KEYWORD          No Operation                  106    PASS
    \END     ITERATION        \${x} = once                  105    PASS
    \END     FOR              \${x} IN once                 105    PASS
    \END     KEYWORD          FOR In Keyword                 26    PASS

FOR in IF
    START    IF               True                           29    NOT SET
    START    FOR              \${x} \${y} IN x y             30    NOT SET
    START    ITERATION        \${x} = x, \${y} = y           30    NOT SET
    START    KEYWORD          No Operation                   31    NOT SET
    \END     KEYWORD          No Operation                   31    PASS
    \END     ITERATION        \${x} = x, \${y} = y           30    PASS
    \END     FOR              \${x} \${y} IN x y             30    PASS
    \END     IF               True                           29    PASS

FOR in resource
    START    KEYWORD          FOR In Resource                36    NOT SET
    START    FOR              \${x} IN once                   6    NOT SET    source=${RESOURCE FILE}
    START    ITERATION        \${x} = once                    6    NOT SET    source=${RESOURCE FILE}
    START    KEYWORD          Log                             7    NOT SET    source=${RESOURCE FILE}
    \END     KEYWORD          Log                             7    PASS       source=${RESOURCE FILE}
    \END     ITERATION        \${x} = once                    6    PASS       source=${RESOURCE FILE}
    \END     FOR              \${x} IN once                   6    PASS       source=${RESOURCE FILE}
    \END     KEYWORD          FOR In Resource                36    PASS

IF
    START    IF               1 > 2                          39    NOT RUN
    START    KEYWORD          Fail                           40    NOT RUN
    \END     KEYWORD          Fail                           40    NOT RUN
    \END     IF               1 > 2                          39    NOT RUN
    START    ELSE IF          1 < 2                          41    NOT SET
    START    KEYWORD          No Operation                   42    NOT SET
    \END     KEYWORD          No Operation                   42    PASS
    \END     ELSE IF          1 < 2                          41    PASS
    START    ELSE             \                              43    NOT RUN
    START    KEYWORD          Fail                           44    NOT RUN
    \END     KEYWORD          Fail                           44    NOT RUN
    \END     ELSE             \                              43    NOT RUN

IF in keyword
    START    KEYWORD          IF In Keyword                  48    NOT SET
    START    IF               True                          110    NOT SET
    START    KEYWORD          No Operation                  111    NOT SET
    \END     KEYWORD          No Operation                  111    PASS
    START    RETURN           ${EMPTY}                      112    NOT SET
    \END     RETURN           ${EMPTY}                      112    PASS
    \END     IF               True                          110    PASS
    \END     KEYWORD          IF In Keyword                  48    PASS

IF in FOR
    START    FOR              \${x} IN 1 2                   52    NOT SET
    START    ITERATION        \${x} = 1                      52    NOT SET
    START    IF               \${x} == 1                     53    NOT SET
    START    KEYWORD          Log                            54    NOT SET
    \END     KEYWORD          Log                            54    PASS
    \END     IF               \${x} == 1                     53    PASS
    START    ELSE             \                              55    NOT RUN
    START    KEYWORD          Fail                           56    NOT RUN
    \END     KEYWORD          Fail                           56    NOT RUN
    \END     ELSE             \                              55    NOT RUN
    \END     ITERATION        \${x} = 1                      52    PASS
    START    ITERATION        \${x} = 2                      52    NOT SET
    START    IF               \${x} == 1                     53    NOT RUN
    START    KEYWORD          Log                            54    NOT RUN
    \END     KEYWORD          Log                            54    NOT RUN
    \END     IF               \${x} == 1                     53    NOT RUN
    START    ELSE             \                              55    NOT SET
    START    KEYWORD          Fail                           56    NOT SET
    \END     KEYWORD          Fail                           56    FAIL
    \END     ELSE             \                              55    FAIL
    \END     ITERATION        \${x} = 2                      52    FAIL
    \END     FOR              \${x} IN 1 2                   52    FAIL

IF in resource
    START    KEYWORD          IF In Resource                 61    NOT SET
    START    IF               True                           11    NOT SET    source=${RESOURCE FILE}
    START    KEYWORD          No Operation                   12    NOT SET    source=${RESOURCE FILE}
    \END     KEYWORD          No Operation                   12    PASS       source=${RESOURCE FILE}
    \END     IF               True                           11    PASS       source=${RESOURCE FILE}
    \END     KEYWORD          IF In Resource                 61    PASS

TRY
    START    TRY              ${EMPTY}                       65    NOT SET
    START    KEYWORD          Fail                           66    NOT SET
    \END     KEYWORD          Fail                           66    FAIL
    \END     TRY              ${EMPTY}                       65    FAIL
    START    EXCEPT           AS \${name}                    67    NOT SET
    START    TRY              ${EMPTY}                       68    NOT SET
    START    KEYWORD          Fail                           69    NOT SET
    \END     KEYWORD          Fail                           69    FAIL
    \END     TRY              ${EMPTY}                       68    FAIL
    START    FINALLY          ${EMPTY}                       70    NOT SET
    START    KEYWORD          Should Be Equal                71    NOT SET
    \END     KEYWORD          Should Be Equal                71    PASS
    \END     FINALLY          ${EMPTY}                       70    PASS
    \END     EXCEPT           AS \${name}                    67    FAIL
    START    ELSE             ${EMPTY}                       73    NOT RUN
    START    KEYWORD          Fail                           74    NOT RUN
    \END     KEYWORD          Fail                           74    NOT RUN
    \END     ELSE             ${EMPTY}                       73    NOT RUN

TRY in keyword
    START    KEYWORD          TRY In Keyword                 78    NOT SET
    START    TRY              ${EMPTY}                      116    NOT SET
    START    RETURN           ${EMPTY}                      117    NOT SET
    \END     RETURN           ${EMPTY}                      117    PASS
    START    KEYWORD          Fail                          118    NOT RUN
    \END     KEYWORD          Fail                          118    NOT RUN
    \END     TRY              ${EMPTY}                      116    PASS
    START    EXCEPT           No match AS \${var}           119    NOT RUN
    START    KEYWORD          Fail                          120    NOT RUN
    \END     KEYWORD          Fail                          120    NOT RUN
    \END     EXCEPT           No match AS \${var}           119    NOT RUN
    START    EXCEPT           No Match 2 AS \${x}           121    NOT RUN
    START    KEYWORD          Fail                          122    NOT RUN
    \END     KEYWORD          Fail                          122    NOT RUN
    \END     EXCEPT           No Match 2 AS \${x}           121    NOT RUN
    START    EXCEPT           ${EMPTY}                      123    NOT RUN
    START    KEYWORD          Fail                          124    NOT RUN
    \END     KEYWORD          Fail                          124    NOT RUN
    \END     EXCEPT           ${EMPTY}                      123    NOT RUN
    \END     KEYWORD          TRY In Keyword                 78    PASS

TRY in resource
    START    KEYWORD          TRY In Resource                81    NOT SET
    START    TRY              ${EMPTY}                       16    NOT SET    source=${RESOURCE FILE}
    START    KEYWORD          Log                            17    NOT SET    source=${RESOURCE FILE}
    \END     KEYWORD          Log                            17    PASS       source=${RESOURCE FILE}
    \END     TRY              ${EMPTY}                       16    PASS       source=${RESOURCE FILE}
    START    FINALLY          ${EMPTY}                       18    NOT SET    source=${RESOURCE FILE}
    START    KEYWORD          Log                            19    NOT SET    source=${RESOURCE FILE}
    \END     KEYWORD          Log                            19    PASS       source=${RESOURCE FILE}
    \END     FINALLY          ${EMPTY}                       18    PASS       source=${RESOURCE FILE}
    \END     KEYWORD          TRY In Resource                81    PASS

Run Keyword
    START    KEYWORD          Run Keyword                    84    NOT SET
    START    KEYWORD          Log                            84    NOT SET
    \END     KEYWORD          Log                            84    PASS
    \END     KEYWORD          Run Keyword                    84    PASS
    START    KEYWORD          Run Keyword If                 85    NOT SET
    START    KEYWORD          User Keyword                   85    NOT SET
    START    KEYWORD          No Operation                  101    NOT SET
    \END     KEYWORD          No Operation                  101    PASS
    START    RETURN           ${EMPTY}                      102    NOT SET
    \END     RETURN           ${EMPTY}                      102    PASS
    \END     KEYWORD          User Keyword                   85    PASS
    \END     KEYWORD          Run Keyword If                 85    PASS

Run Keyword in keyword
    START    KEYWORD          Run Keyword in keyword         89    NOT SET
    START    KEYWORD          Run Keyword                   128    NOT SET
    START    KEYWORD          No Operation                  128    NOT SET
    \END     KEYWORD          No Operation                  128    PASS
    \END     KEYWORD          Run Keyword                   128    PASS
    \END     KEYWORD          Run Keyword in keyword         89    PASS

Run Keyword in resource
    START    KEYWORD          Run Keyword in resource        92    NOT SET
    START    KEYWORD          Run Keyword                    23    NOT SET    source=${RESOURCE FILE}
    START    KEYWORD          Log                            23    NOT SET    source=${RESOURCE FILE}
    \END     KEYWORD          Log                            23    PASS       source=${RESOURCE FILE}
    \END     KEYWORD          Run Keyword                    23    PASS       source=${RESOURCE FILE}
    \END     KEYWORD          Run Keyword in resource        92    PASS

In setup and teardown
    START    SETUP            User Keyword                   95    NOT SET
    START    KEYWORD          No Operation                  101    NOT SET
    \END     KEYWORD          No Operation                  101    PASS
    START    RETURN           ${EMPTY}                      102    NOT SET
    \END     RETURN           ${EMPTY}                      102    PASS
    \END     SETUP            User Keyword                   95    PASS
    START    KEYWORD          No Operation                   96    NOT SET
    \END     KEYWORD          No Operation                   96    PASS
    START    TEARDOWN         Run Keyword                    97    NOT SET
    START    KEYWORD          Log                            97    NOT SET
    \END     KEYWORD          Log                            97    PASS
    \END     TEARDOWN         Run Keyword                    97    PASS

Suite
    START    SUITE            Lineno And Source
    \END     SUITE            Lineno And Source                               status=FAIL
    [Teardown]    Validate suite

Test
    [Template]    Expect test
    Keyword                                                   5
    User keyword                                              8
    User keyword in resource                                 11
    Not run keyword                                          14    FAIL
    \FOR                                                     20
    FOR in keyword                                           25
    FOR in IF                                                28
    FOR in resource                                          35
    \IF                                                      38
    IF in keyword                                            47
    IF in FOR                                                50    FAIL
    IF in resource                                           60
    \TRY                                                     63    FAIL
    TRY in keyword                                           77
    TRY in resource                                          80
    Run Keyword                                              83
    Run Keyword in keyword                                   88
    Run Keyword in resource                                  91
    In setup and teardown                                    94
    [Teardown]    Validate tests

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
