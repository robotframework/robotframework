*** Settings ***
Documentation      Tests for --test and --suite options.
Resource           atest_resource.robot

*** Variables ***
${SUITE FILE}      misc/many_tests.robot
${SUITE DIR}       misc/suites

*** Test Cases ***
--test once
    Run And Check Tests    --test First    First

--test multiple times
    Run And Check Tests    --test first --test nomatch -t "sec_ _ondONE"    First    Second One

--test with patterns
    Run And Check Tests    --test *one --test Fi?st    First    Second One    Third One
    Run And Check Tests    --test [Great]Lob[sterB]estCase[!3-9]    GlobTestCase1    GlobTestCase2

--test not matching
    Run Failing Test
    ...    Suite 'Many Tests' contains no tests matching name 'notexists'.
    ...    --test notexists

--test not matching with multiple inputs
    Run Failing Test
    ...    Suite 'Many Tests & Suites' contains no tests matching name 'notexists'.
    ...    --test notexists    ${SUITE FILE} ${SUITE DIR}
    Run Failing Test
    ...    Suite 'My Name' contains no tests matching name 'notexists'.
    ...    --name "My Name" --test notexists    ${SUITE FILE} ${SUITE DIR}

--test and --include must both match
    Run And Check Tests    --test first --include t1 -i f1    First
    Run Failing Test
    ...    Suite 'Many Tests' contains no tests matching name 'fifth' and matching tag 't1'.
    ...    --test fifth --include t1

--exclude wins over --test
    Run And Check Tests    --test fi* --exclude t1    Fifth
    Run Failing Test
    ...    Suite 'Many Tests' contains no tests matching name 'first' and not matching tag 'f1'.
    ...    --test first --exclude f1

--suite once
    Run Suites    --suite tsuite1
    Should Contain Suites   ${SUITE}    TSuite1
    Should Contain Tests    ${SUITE}   Suite1 First    Suite1 Second    Third In Suite1

--suite with . in name
    Run Suites    --suite sub.suite.4
    Should Contain Suites    ${SUITE}    Custom name for 📂 'subsuites2'
    Should Contain Tests   ${SUITE}    Test From Sub Suite 4
    Should Not Contain Tests    ${SUITE}   SubSuite3 First    SubSuite3 Second

--suite multiple times
    Run Suites    --suite "t_ _SuiTe_1" --suite NoMatch -s tsuite2
    Should Contain Suites    ${SUITE}    Tsuite1   Tsuite2
    Should Contain Tests    ${SUITE}   Suite1 First    Suite1 Second    Third In Suite1    Suite2 First

--suite with patterns
    Run Suites    --suite t*te[13] -s [foo][foo]urth
    Should Contain Suites    ${SUITE}    Tsuite1    Tsuite3    Fourth
    Should Contain Tests   ${SUITE}    Suite1 First    Suite1 Second    Third In Suite1    Suite3 First    Suite4 First

Parent suite init files are processed
    Previous Test Should Have Passed    --suite with patterns
    Should Be True    ${SUITE.teardown}
    Check log message    ${SUITE.teardown.msgs[0]}    Default suite teardown

--suite matching directory
    Run Suites    --suite sub?uit[efg]s
    Should Contain Suites    ${SUITE.suites[0]}    Sub1    Sub2
    Should Contain Tests   ${SUITE}    SubSuite1 First    SubSuite2 First

--suite with long name matching file
    Run Suites    --suite suites.fourth --suite suites.*.SUB?
    Should Contain Suites    ${SUITE}    Fourth    Subsuites
    Should Contain Tests   ${SUITE}    Suite4 First    SubSuite1 First    SubSuite2 First

--suite with long name matching directory
    Run Suites    --suite suites.subsuites
    Should Contain Suites    ${SUITE}    Subsuites
    Should Contain Suites    ${SUITE.suites[0]}    Sub1    Sub2
    Should Contain Tests   ${SUITE}    SubSuite1 First    SubSuite2 First

--suite with long name with . in name
    Run Suites    --suite "suites.Custom name for 📂 'subsuites2'.sub.suite.4"
    Should Contain Suites    ${SUITE}    Custom name for 📂 'subsuites2'
    Should Contain Tests   ${SUITE}    Test From Sub Suite 4
    Should Not Contain Tests    ${SUITE}   SubSuite3 First    SubSuite3 Second

--suite matching end of long name is not enough anymore
    [Documentation]    This was supported until RF 7.0.
    Run Failing Test
    ...    Suite 'Suites' contains no tests in suite 'Subsuites.Sub?'.
    ...    --suite Subsuites.Sub?    ${SUITE DIR}

--suite with long name when executing multiple suites
    Run Suites    -s "Suite With Prefix & Subsuites.Subsuites.Sub1"    misc/suites/01__suite_with_prefix misc/suites/subsuites
    Should Contain Suites    ${SUITE}              Subsuites
    Should Contain Suites    ${SUITE.suites[0]}    Sub1
    Should Contain Tests     ${SUITE}              SubSuite1 First

--suite with long name and --name
    Run Suites    --name Custom --suite custom.fourth
    Should Contain Suites    ${SUITE}    fourth
    Should Contain Tests     ${SUITE}    Suite4 First

--suite not matching
    Run Failing Test
    ...    Suite 'Suites' contains no tests in suite 'notexists'.
    ...    --suite notexists    ${SUITE DIR}

--suite not matching with multiple inputs
    Run Failing Test
    ...    Suite 'Suites & Many Tests' contains no tests in suite 'notexists'.
    ...    --suite notexists    ${SUITE DIR} ${SUITE FILE}
    Run Failing Test
    ...    Suite 'Custom' contains no tests in suite 'xxx'.
    ...    --suite xxx -N Custom    ${SUITE DIR} ${SUITE FILE}

--suite and --test together
    [Documentation]    Validate that only tests matching --test under suites matching --suite are selected.
    Run Suites    --suite suites.subsuites.sub2 --suite tsuite3 --test *First
    Should Contain Suites    ${SUITE}    Subsuites    Tsuite3
    Should Contain Tests     ${SUITE}    SubSuite2 First    Suite3 First

--suite and --test together not matching
    Run Failing Test
    ...    Suite 'Suites' contains no tests matching name 'Suite1*' or 'nomatch' in suites 'subsuites' or 'nomatch'.
    ...    --suite subsuites -s nomatch --test Suite1* -t nomatch    ${SUITE DIR}

--suite with --include/--exclude
    Run Suites    --suite tsuite[13] --include t? --exclude t2
    Should Contain Suites    ${SUITE}    Tsuite1    Tsuite3
    Should Contain Tests     ${SUITE}    Suite1 First    Suite3 First

--suite, --test, --include and --exclude
    Run Suites    --suite sub* --suite "custom name *" --test "subsuite3 second" -t *first -s nomatch -t nomatch --include f1 --exclude t1
    Should Contain Suites    ${SUITE}    Custom name for 📂 'subsuites2'    Subsuites
    Should Contain Tests     ${SUITE}    SubSuite2 First    SubSuite3 Second

--suite with long name and other filters
    Run Suites    --suite suites.fourth --suite tsuite1 -s *.Subsuites.Sub1 --test *first* --exclude none
    Should Contain Suites    ${SUITE}   Fourth    Subsuites    Tsuite1
    Should Contain Tests   ${SUITE}    Suite4 First    Suite1 First    SubSuite1 First

--suite when files have ordering prefixes
    Run Suites    --suite sub.suite.1 -s mu*_su*.suite[5-6] --exclude warning    misc/multiple_suites
    Should Contain Suites    ${SUITE}   Sub.Suite.1    Suite5    Suite6
    Should Contain Suites    ${SUITE.suites[0]}   .Sui.te.2.    Suite4

Suite containing tasks is ok if only tests are selected
    Run And Check Tests    --test test      Test    sources=rpa/tasks rpa/tests.robot
    Run And Check Tests    --suite tests    Test    sources=rpa/tasks rpa/tests.robot

*** Keywords ***
Run And Check Tests
    [Arguments]    ${params}    @{tests}    ${sources}=${SUITE FILE}
    Run Tests    ${params}    ${sources}
    Stderr Should Be Empty
    Should Contain Tests    ${suite}    @{tests}

Run Suites
    [Arguments]    ${options}    ${testdata}=${SUITE DIR}
    Run Tests    ${options}    ${testdata}
    Stderr Should Be Empty

Run Failing Test
    [Arguments]    ${error}    ${options}    ${sources}=${SUITE FILE}
    Run Tests Without Processing Output    ${options}    ${sources}
    Stderr Should Be Equal To    [ ERROR ] ${error}${USAGE TIP}\n
