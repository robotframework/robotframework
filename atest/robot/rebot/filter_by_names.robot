*** Settings ***
Documentation     Testing --test and --suite options with Rebot.
Suite Setup       Create Input File
Suite Teardown    Remove Temps
Test Setup        Empty Directory    ${MYOUTDIR}
Resource          rebot_resource.robot

*** Variables ***
${SUITE FILE}     misc${/}many_tests.robot
${SUITE DIR}      misc${/}suites
${MYOUTDIR}       %{TEMPDIR}${/}robot-test-145567
${INPUT FILE}     %{TEMPDIR}${/}robot-test-file.xml

*** Test Cases ***
One Call To Test
    Run And Check Tests    --test First    First

One Call To Test With Normalized Test Name
    Run And Check Tests    --test secondone    Second One

Two Calls To test
    Run And Check Tests    --test First --test thirdone    First    Third One

Two Calls to Test with one nonexisting test name
    Run And Check Tests    --test notexists --test First    First

One Call To test with pattern
    Run And Check Tests    --test *one*    Second One    Third One    Fourth One With More Complex Name

Two Calls To test with patterns
    Run And Check Tests    --test *one --test Fi?st    First    Second One    Third One

Test Filtering With Glob Bracket
    Run And Check Tests    --test [Great]Lob[sterB]estCase[1-2]    GlobTestCase1    GlobTestCase2

Test Filtering With Negative Glob Bracket
    Run And Check Tests    --test Glob[!BAD]est*[!1-3]    GlobTestCase[5]    GlobTest Cat    GlobTest Rat

Suite With One Arg
    Run And Check Suites    --suite tsuite1   Tsuite1

Suite with two args
    Run And Check Suites    --suite tsuite1 --suite TSuite2   Tsuite1    Tsuite2

Suite With Matching and nonMatching args
    Run And Check Suites    --suite tsuite1 --suite notexists   Tsuite1

Suite With Pattern in arg
    Run And Check Suites    --suite t*    Tsuite1   Tsuite2   Tsuite3

Suite Under Subdirectory
    Run And Check Suites Within Subdirs    --suite sub1   Sub1

Suite Under Subdirectory Using Pattern
    Run And Check Suites Within Subdirs    --suite sub?    Sub1    Sub2

Suite and test together
    Run And Check Suites and Tests    --suite tsuite1 --suite tsuite3 --test *1first --test *2*    Tsuite1    Suite1 First

No matching tests
    Failing Rebot
    ...    Suite 'Many Tests & Suites' contains no tests named 'nonex'.
    ...    --test nonex    ${INPUT FILE}

No matching tests when reboting multiple inputs
    Failing Rebot
    ...    Suite 'Many Tests & Suites & Many Tests & Suites' contains no tests named 'nonex'.
    ...    --test nonex    ${INPUT FILE} ${INPUT FILE}
    Failing Rebot
    ...    Suite 'My Name' contains no tests named 'nonex'.
    ...    --test nonex -N "My Name"    ${INPUT FILE} ${INPUT FILE}

No matching suites
    Failing Rebot
    ...    Suite 'Many Tests & Suites' contains no tests in suites 'nonex', 'n2' or 'n3'.
    ...    --suite nonex -s n2 -s n3    ${INPUT FILE}

No matching suites when reboting multiple inputs
    Failing Rebot
    ...    Suite 'Many Tests & Suites & Many Tests & Suites' contains no tests in suite 'nonex'.
    ...    --suite nonex    ${INPUT FILE} ${INPUT FILE}
    Failing Rebot
    ...    Suite 'CustomName' contains no tests in suite 'nonex'.
    ...    --name CustomName --suite nonex    ${INPUT FILE} ${INPUT FILE}

No Matching Tests In Matching Suites
    Failing Rebot
    ...     Suite 'Many Tests & Suites' contains no tests named 'first', 'nonex' or '*one' in suites 'nonex' or 'suites'.
    ...    --suite nonex --suite suites --test first --test nonex --test *one    ${INPUT FILE}

Elapsed Time
    [Documentation]    Test setting start, end and elapsed times correctly when filtering by tags
    Comment    1) Rebot hand-edited output with predefined times and    check that times are read correctly. (A sanity check)
    Run Rebot    ${EMPTY}    rebot${/}times.xml
    Check Times    ${SUITE.tests[0]}    20061227 12:00:00.000    20061227 12:00:01.000    1000    # Incl-1
    Check Times    ${SUITE.tests[1]}    20061227 12:00:01.000    20061227 12:00:03.000    2000    # Incl-12
    Check Times    ${SUITE.tests[2]}    20061227 12:00:03.000    20061227 12:00:07.000    4000    # Incl-123
    Check Times    ${SUITE.tests[3]}    20061227 12:00:07.000    20061227 12:00:07.001    0001    # Excl-1
    Check Times    ${SUITE.tests[4]}    20061227 12:00:07.001    20061227 12:00:07.003    0002    # Excl-12
    Check Times    ${SUITE.tests[5]}    20061227 12:00:07.003    20061227 12:00:07.007    0004    # Excl-123
    Check Times    ${SUITE}    20061227 11:59:59.000    20061227 12:00:08.999    9999    # Suite
    Should Be Equal As Integers    ${SUITE.test_count}    6
    Comment    2) Filter output created in earlier step and check    that times are set accordingly.
    Copy Previous Outfile
    Run Rebot    --test Exc* --test Incl-1    ${OUTFILE COPY}
    Check Times    ${SUITE.tests[0]}    20061227 12:00:00.000    20061227 12:00:01.000    1000    # Incl-1
    Check Times    ${SUITE.tests[1]}    20061227 12:00:07.000    20061227 12:00:07.001    0001    # Excl-1
    Check Times    ${SUITE.tests[2]}    20061227 12:00:07.001    20061227 12:00:07.003    0002    # Excl-12
    Check Times    ${SUITE.tests[3]}    20061227 12:00:07.003    20061227 12:00:07.007    0004    # Excl-123
    Check Times    ${SUITE}    ${NONE}    ${NONE}    1007    # Suite
    Should Be Equal As Integers    ${SUITE.test_count}    4

*** Keywords ***
Create Input File
    Create Output With Robot    ${INPUT FILE}    ${EMPTY}    ${SUITE FILE} ${SUITE DIR}
    Create Directory    ${MYOUTDIR}

Remove Temps
    Remove Directory    ${MYOUTDIR}    recursive
    Remove FIle    ${INPUT FILE}

Run and check Tests
    [Arguments]    ${params}    @{tests}
    Run Rebot    ${params}    ${INPUT FILE}
    Stderr Should Be Empty
    Should Contain Tests    ${SUITE}    @{tests}
    Should Be True    ${SUITE.statistics.all.passed} == len(@{tests})
    Check Stats

Check Stats
    Should Be True    ${SUITE.statistics.all.failed} == 0
    Should Be Equal    ${SUITE.starttime}    ${NONE}
    Should Be Equal    ${SUITE.endtime}    ${NONE}
    Elapsed Time Should Be Valid    ${SUITE.elapsedtime}
    Should Be True    ${SUITE.elapsedtime} <= ${ORIGELAPSED}

Run and Check Suites
    [Arguments]    ${params}    @{suites}
    Run Suites    ${params}
    Should Contain Suites    ${SUITE.suites[0]}    @{suites}
    Check Stats

Run and check suites within subdirs
    [Arguments]    ${params}    @{suites}
    Run Suites    ${params}
    Should Contain Suites    ${SUITE.suites[0].suites[0]}   @{suites}
    Check Stats

Run And Check Suites and Tests
    [Arguments]    ${params}    ${subsuite}    @{tests}
    Run Suites    ${params}
    Should Contain Suites    ${SUITE.suites[0]}   ${subsuite}
    Should Contain Tests    ${SUITE}    @{tests}
    Should Be True    ${SUITE.statistics.all.passed} == len(@{tests})
    Check Stats

Run Suites
    [Arguments]    ${options}
    Run Rebot    ${options}    ${INPUT FILE}
    Stderr Should Be Empty

Failing Rebot
    [Arguments]    ${error}    ${options}    ${sources}
    Run Rebot Without Processing Output    ${options}    ${sources}
    Stderr Should Be Equal To    [ ERROR ] ${error}${USAGE TIP}\n
