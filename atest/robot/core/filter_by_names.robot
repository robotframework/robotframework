*** Settings ***
Documentation      Tests for --test and --suite options.
Resource           atest_resource.robot

*** Variables ***
${SUITE FILE}      misc/many_tests.robot
${SUITE DIR}       misc/suites

*** Test Cases ***
One Call To Test
    Run And Check Tests    --test First    First

Test Name With Spaces, Underscores And Mixed Case
    [Documentation]    Testing that spaces, underscores and case are ignored in suite names.
    Run And Check Tests    --test "sec_ _ondONE"    Second One

One Call To Test With Normalized Test Name
    Run And Check Tests    --test secondone    Second One

Two Calls To Test
    Run And Check Tests    --test First --test thirdone    First    Third One

Non-Existing Test
    Run Failing Test
    ...    Suite 'Many Tests' contains no tests named 'notexists'.
    ...    --test notexists    ${SUITE FILE}

Non-Existing Test When Running Multiple Suites
    Run Failing Test
    ...    Suite 'Many Tests & Suites' contains no tests named 'notexists'.
    ...    --test notexists    ${SUITE FILE} ${SUITE DIR}
    Run Failing Test
    ...    Suite 'My Name' contains no tests named 'notexists'.
    ...    --name "My Name" --test notexists    ${SUITE FILE} ${SUITE DIR}

Two Calls To Test With One Nonexisting Test Name
    Run And Check Tests    --test notexists --test First    First

One Call To Test With Pattern
    Run And Check Tests    --test *one*    Second One    Third One    Fourth One With More Complex Name

Two Calls To Test With Patterns
    Run And Check Tests    --test *one --test Fi?st    First    Second One    Third One

Test Filtering With Glob Bracket
    Run And Check Tests    --test [Great]Lob[sterB]estCase[1-2]    GlobTestCase1    GlobTestCase2

Test Filtering With Negative Glob Bracket
    Run And Check Tests    --test Glob[!BAD]est*[!1-3]    GlobTestCase[5]    GlobTest Cat    GlobTest Rat

Suite With One Arg
    Run Suites    --suite tsuite1
    Should Contain Suites   ${SUITE}    TSuite1
    Should Contain Tests    ${SUITE}   Suite1 First    Suite1 Second    Third In Suite1

Suite Name With Spaces, Underscores And Mixed Case
    [Documentation]    Testing that spaces, underscores and case are ignored in suite names.
    Run Suites    --suite "t_ _SuiTe_1"
    Should Contain Suites   ${SUITE}    TSuite1
    Should Contain Tests   ${SUITE}    Suite1 First    Suite1 Second    Third In Suite1

Suite Name With Dot
    Run Suites    --suite suites.subsuites2.sub.suite.4
    Should Contain Suites    ${SUITE}    Subsuites2
    Should Contain Tests   ${SUITE}    Test From Sub Suite 4
    Should Not Contain Tests    ${SUITE}   SubSuite3 First    SubSuite3 Second

Suite With Two Args
    Run Suites    --suite tsuite1 --suite TSuite2
    Should Contain Suites    ${SUITE}    Tsuite1   Tsuite2
    Should Contain Tests    ${SUITE}   Suite1 First    Suite1 Second    Third In Suite1    Suite2 First

Parent suite init files are processed
    Should Be True    ${SUITE.teardown}
    Check log message    ${SUITE.teardown.msgs[0]}    Default suite teardown

Correct Files Processed With --suite Matches Files
    [Documentation]    Test that only files matching --suite are processed.
    ...                Additionally __init__ files should never be ignored.
    ${root} =    Normalize Path    ${DATA DIR}/${SUITE DIR}
    Check Syslog Contains    Parsing test data directory '${root}'
    Check Syslog Contains    Ignoring file or directory 'fourth.robot'
    Check Syslog Contains    Ignoring file or directory 'tsuite3.robot'
    Check Syslog Contains    Parsing test data directory '${root}${/}subsuites'
    Check Syslog Contains    Ignoring file or directory 'sub1.robot'
    Check Syslog Contains    Ignoring file or directory 'sub2.robot'
    Check Syslog Contains    Parsing file '${root}${/}tsuite1.robot
    Check Syslog Contains    Parsing file '${root}${/}tsuite2.robot
    Check Syslog Does Not Contain    Ignoring file or directory '__init__.robot'

Non-Existing Suite
    Run Failing Test
    ...    Suite 'Suites' contains no tests in suite 'notexists'.
    ...    --suite notexists    ${SUITE DIR}

Non-Existing Suite When Running Multiple Suites
    Run Failing Test
    ...    Suite 'Suites & Many Tests' contains no tests in suite 'notexists'.
    ...    --suite notexists    ${SUITE DIR} ${SUITE FILE}
    Run Failing Test
    ...    Suite 'Custom' contains no tests in suite 'xxx'.
    ...    --suite xxx -N Custom    ${SUITE DIR} ${SUITE FILE}

Suite With Matching And NonMatching Args
    Run Suites    --suite tsuite1 --suite notexists
    Should Contain Suites   ${SUITE}    TSuite1
    Should Contain Tests   ${SUITE}    Suite1 First    Suite1 Second    Third In Suite1

Suite With Pattern In Arg
    Run Suites    --suite t*
    Should Contain Suites    ${SUITE}    Tsuite1    Tsuite2    Tsuite3
    Should Contain Tests   ${SUITE}    Suite1 First    Suite1 Second    Third In Suite1    Suite2 First    Suite3 First

Selecting Directory Suite
    Run And Check Suites Within Subdirs    --suite subsuites    Sub1    Sub2
    Should Contain Tests   ${SUITE.suites[0]}    SubSuite1 First    SubSuite2 First

Correct Files Processed When --suite Matches Directory
    [Documentation]    Testing that only files matching to --suite are processed.
    ...                This time --suite matches directory so all suites under it
    ...                should be processed. Using data from previous test case.
    ${suitedir} =    Join Path    ${DATA DIR}    ${SUITE DIR}
    ${subsuitedir} =    Join Path    ${suitedir}    subsuites
    Check Syslog Contains    Parsing test data directory '${suitedir}'
    Check Syslog Contains    Ignoring file or directory 'fourth.robot'
    Check Syslog Contains    Ignoring file or directory 'tsuite1.robot'
    Check Syslog Contains    Ignoring file or directory 'tsuite2.robot'
    Check Syslog Contains    Ignoring file or directory 'tsuite3.robot'
    Check Syslog Contains    Parsing test data directory '${subsuitedir}'
    Check Syslog Contains    Parsing file '${subsuitedir}${/}sub1.robot'
    Check Syslog Contains    Parsing file '${subsuitedir}${/}sub2.robot'

Suite Under Subdirectory Using Pattern
    Run And Check Suites Within Subdirs    --suite sub?    Sub1    Sub2
    Should Contain Tests   ${SUITE.suites[0]}    SubSuite1 First    SubSuite2 First

Suite And Test Together
    [Documentation]    Testing that only tests matching --test which are under suite matching --suite are run.
    Run Suites    --suite subsuites --suite tsuite3 --test SubSuite1First
    Should Contain Suites    ${SUITE}    Subsuites
    Should Contain Tests   ${SUITE}    SubSuite1 First

Suite With Include And Exclude
    Run Suites    --suite tsuite? --include t* --exclude t2
    Should Contain Suites    ${SUITE}    Tsuite1    Tsuite2    Tsuite3
    Should Contain Tests    ${SUITE}    Suite1 First    Suite2 First    Suite3 First

Suite, Test Include And Exclude Together
    Run Suites    --suite sub* --test *first -s nosuite -t notest --include t1 --exclude sub3
    Should Contain Suites   ${SUITE}    Subsuites
    Should Contain Tests    ${SUITE}    SubSuite1 First

Filter Using Suite Long Name
    Run Suites    --suite suites.fourth
    Should Contain Suites    ${SUITE}    Fourth
    Should Contain Tests   ${SUITE}    Suite4 First
    Run Suites    --suite Subsuites.Sub1
    Should Contain Suites    ${SUITE}    Subsuites
    Should Contain Tests   ${SUITE}   SubSuite1 First
    Run Suites    --suite child_suite1.test  ${DATA DIR}/misc/parent_suite
    Should Contain Suites   ${SUITE}  Child Suite 1
    Stderr Should Be Empty

Filter Using Long Suite Name WIth Pattern
    Run Suites    --suite suites.*.SUB?
    Should Contain Suites    ${SUITE}   Subsuites
    Should Contain Tests   ${SUITE}   SubSuite1 First    SubSuite2 First

Filter Using Long Suite Name And Other Filters
    Run Suites    --suite suites.fourth --suite tsuite1 -s Subsuites.Sub1 --test *first* --exclude none
    Should Contain Suites    ${SUITE}   Fourth    Subsuites    Tsuite1
    Should Contain Tests   ${SUITE}    Suite4 First    Suite1 First    SubSuite1 First

Filter Suite When Suites Are Ordered With Prefix
    Run Suites    --suite ?Sui*2?    ${DATA DIR}/misc/multiple_suites
    Should Contain Suites   ${SUITE}   Sub.Suite.1
    Should Contain Suites   ${SUITE.suites[0]}    .Sui.te.2.

*** Keywords ***
Run And Check Tests
    [Arguments]    ${params}    @{tests}
    Run Tests    ${params}    ${SUITE FILE}
    Stderr Should Be Empty
    Should Contain Tests    ${suite}    @{tests}

Run And Check Suites Within Subdirs
    [Arguments]    ${params}    @{suites}
    Run Suites    ${params}
    Should Contain Suites    ${SUITE.suites[0]}    @{suites}

Run Suites
    [Arguments]    ${options}    ${testdata}=${SUITE DIR}
    Run Tests    ${options}    ${testdata}
    Stderr Should Be Empty

Run Failing Test
    [Arguments]    ${error}    ${options}    ${sources}
    Run Tests Without Processing Output    ${options}    ${sources}
    Stderr Should Be Equal To    [ ERROR ] ${error}${USAGE TIP}\n
