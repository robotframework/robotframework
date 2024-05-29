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
--test once
    Run And Check Tests    --test First    First

--test multiple times
    Run And Check Tests    --test first --test nomatch -t "sec_ _ondONE"    First    Second One

--test with patterns
    Run And Check Tests    --test *one --test Fi?st    First    Second One    Third One
    Run And Check Tests    --test [Great]Lob[sterB]estCase[!3-9]    GlobTestCase1    GlobTestCase2

--test not matching
    Failing Rebot
    ...    Suite 'Root' contains no tests matching name 'nonex'.
    ...    --test nonex

--test not matching with multiple inputs
    Failing Rebot
    ...    Suite 'Root & Root' contains no tests matching name 'nonex'.
    ...    --test nonex    ${INPUT FILE} ${INPUT FILE}
    Failing Rebot
    ...    Suite 'My Name' contains no tests matching name 'nonex'.
    ...    --test nonex -N "My Name"    ${INPUT FILE} ${INPUT FILE}

--test and --include must both match
    Run And Check Tests    --test first --include t1 -i f1    First
    Failing Rebot
    ...    Suite 'Root' contains no tests matching name 'fifth' and matching tag 't1'.
    ...    --test fifth --include t1

--exclude wins over --test
    Run And Check Tests    --test fi* --exclude t1    Fifth
    Failing Rebot
    ...    Suite 'Root' contains no tests matching name 'first' and not matching tag 'f1'.
    ...    --test first --exclude f1

--suite once
    Run And Check Suites    --suite tsuite1   Tsuite1

--suite multiple times
    Run And Check Suites    --suite "t suite 1" -s nomatch -s T_Suite_2    Tsuite1    Tsuite2

--suite with patterns
    Run And Check Suites    --suite t*te?    Tsuite1   Tsuite2   Tsuite3

--suite with long name
    Run And Check Suites    --suite root.many_tests
    Should Contain Suites    ${SUITE}    Many Tests
    Run And Check Suites    --suite Root.*.SubSuites    Subsuites
    Should Contain Suites    ${SUITE}    Suites
    Should Contain Suites    ${SUITE.suites[0].suites[0]}    Sub1    Sub2

--suite matching end of long name is not enough anymore
    [Documentation]    This was supported until RF 7.0.
    Failing Rebot
    ...    Suite 'Root' contains no tests in suite 'suites.subsuites'.
    ...    --suite suites.subsuites    ${INPUT FILE}

--suite not matching
    Failing Rebot
    ...    Suite 'Root' contains no tests in suites 'nonex', 'n2' or 'n3'.
    ...    --suite nonex -s n2 -s n3    ${INPUT FILE}

--suite not matching with multiple inputs
    Failing Rebot
    ...    Suite 'Root & Root' contains no tests in suite 'nonex'.
    ...    --suite nonex    ${INPUT FILE} ${INPUT FILE}
    Failing Rebot
    ...    Suite 'CustomName' contains no tests in suite 'nonex'.
    ...    --name CustomName --suite nonex    ${INPUT FILE} ${INPUT FILE}

--suite and --test together
    [Documentation]    Validate that only tests matching --test under suites matching --suite are selected.
    Run Suites    --suite root.*.tsuite2 --suite manytests --test *first* --test nomatch --log log
    Should Contain Suites    ${SUITE}              Many Tests    Suites
    Should Contain Tests     ${SUITE.suites[0]}    First
    Should Contain Tests     ${SUITE.suites[1]}    Suite2 First
    Check Stats

--suite and --test together not matching
    Failing Rebot
    ...     Suite 'Root' contains no tests matching name 'first', 'nonex' or '*one' in suites 'nonex' or 'suites'.
    ...    --suite nonex --suite suites --test first --test nonex --test *one    ${INPUT FILE}

--suite with --include/--exclude
    Run Suites    --suite tsuite[13] --include t? --exclude t2
    Should Contain Suites    ${SUITE}              Suites
    Should Contain Suites    ${SUITE.suites[0]}    Tsuite1    Tsuite3
    Should Contain Tests     ${SUITE}              Suite1 First    Suite3 First

--suite, --test, --include and --exclude
    Run Suites    --suite sub* --suite "custom name *" --test "subsuite3 second" -t *first -s nomatch -t nomatch --include f1 --exclude t1
    Should Contain Suites    ${SUITE}              Suites
    Should Contain Suites    ${SUITE.suites[0]}    Custom name for 📂 'subsuites2'    Subsuites
    Should Contain Tests     ${SUITE}              SubSuite2 First    SubSuite3 Second

Elapsed Time
    [Documentation]    Test setting start, end and elapsed times correctly when filtering by tags
    # 1) Rebot hand-edited output with predefined times and check that times are read correctly. (A sanity check)
    Run Rebot    ${EMPTY}    rebot${/}times.xml
    Times Should Be    ${SUITE.tests[0]}    2006-12-27 12:00:00.000    2006-12-27 12:00:01.000    1.000    # Incl-1
    Times Should Be    ${SUITE.tests[1]}    2006-12-27 12:00:01.000    2006-12-27 12:00:03.000    2.000    # Incl-12
    Times Should Be    ${SUITE.tests[2]}    2006-12-27 12:00:03.000    2006-12-27 12:00:07.000    4.000    # Incl-123
    Times Should Be    ${SUITE.tests[3]}    2006-12-27 12:00:07.000    2006-12-27 12:00:07.001    0.001    # Excl-1
    Times Should Be    ${SUITE.tests[4]}    2006-12-27 12:00:07.001    2006-12-27 12:00:07.003    0.002    # Excl-12
    Times Should Be    ${SUITE.tests[5]}    2006-12-27 12:00:07.003    2006-12-27 12:00:07.007    0.004    # Excl-123
    Times Should Be    ${SUITE}             2006-12-27 11:59:59.000    2006-12-27 12:00:08.999    9.999    # Suite
    Should Be Equal As Integers    ${SUITE.test_count}    6
    # 2) Filter output created in earlier step and check that times are set accordingly.
    Copy Previous Outfile
    Run Rebot    --test Exc* --test Incl-1    ${OUTFILE COPY}
    Times Should Be    ${SUITE.tests[0]}    2006-12-27 12:00:00.000    2006-12-27 12:00:01.000    1.000    # Incl-1
    Times Should Be    ${SUITE.tests[1]}    2006-12-27 12:00:07.000    2006-12-27 12:00:07.001    0.001    # Excl-1
    Times Should Be    ${SUITE.tests[2]}    2006-12-27 12:00:07.001    2006-12-27 12:00:07.003    0.002    # Excl-12
    Times Should Be    ${SUITE.tests[3]}    2006-12-27 12:00:07.003    2006-12-27 12:00:07.007    0.004    # Excl-123
    Times Should Be    ${SUITE}             ${NONE}                    ${NONE}                    1.007    # Suite
    Should Be Equal As Integers    ${SUITE.test_count}    4

*** Keywords ***
Create Input File
    Create Output With Robot    ${INPUT FILE}    --name Root    ${SUITE FILE} ${SUITE DIR}
    Create Directory    ${MYOUTDIR}

Remove Temps
    Remove Directory    ${MYOUTDIR}    recursive
    Remove File    ${INPUT FILE}

Run and Check Tests
    [Arguments]    ${params}    @{tests}
    Run Rebot    ${params}    ${INPUT FILE}
    Stderr Should Be Empty
    Should Contain Tests    ${SUITE}    @{tests}
    Should Be True    ${SUITE.statistics.passed} == len(@{tests})
    Check Stats

Check Stats
    Should Be True    ${SUITE.statistics.failed} == 0
    Should Be Equal    ${SUITE.start_time}    ${NONE}
    Should Be Equal    ${SUITE.end_time}    ${NONE}
    Elapsed Time Should Be Valid    ${SUITE.elapsed_time}    maximum=${ORIG_ELAPSED.total_seconds()}

Run and Check Suites
    [Arguments]    ${params}    @{suites}
    Run Suites    ${params}
    Should Contain Suites    ${SUITE.suites[0]}    @{suites}
    Check Stats

Run Suites
    [Arguments]    ${options}
    Run Rebot    ${options}    ${INPUT FILE}
    Stderr Should Be Empty

Failing Rebot
    [Arguments]    ${error}    ${options}    ${sources}=${INPUT FILE}
    Run Rebot Without Processing Output    ${options}    ${sources}
    Stderr Should Be Equal To    [ ERROR ] ${error}${USAGE TIP}\n
