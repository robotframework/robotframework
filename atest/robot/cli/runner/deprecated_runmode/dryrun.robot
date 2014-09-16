*** Settings ***
Suite Setup     Run Tests  --runmode dryrun  cli/dryrun/dryrun.robot  cli/dryrun/more_tests.robot
Force Tags      regression  pybot  jybot
Resource        atest_resource.robot

*** Test Cases ***

Passing keywords
    ${tc}=  Check Test Case  ${TESTNAME}
    Should have correct number of keywords  ${tc}  3
    Name and status should be  ${tc.kws[0]}  BuiltIn.Log  NOT_RUN
    Name and status should be  ${tc.kws[1]}  \${contents} = OperatingSystem.List Directory  NOT_RUN
    Name and status should be  ${tc.kws[2]}  resource.Simple UK  PASS
    Name and status should be  ${tc.kws[2].kws[0]}  BuiltIn.Log  NOT_RUN

Keywords with embedded arguments
    ${tc}=  Check Test Case  ${TESTNAME}
    Should have correct number of keywords  ${tc}  2
    Name and status should be  ${tc.kws[0]}  Embedded arguments here  PASS
    Name and status should be  ${tc.kws[0].kws[0]}  BuiltIn.No Operation  NOT_RUN
    Name and status should be  ${tc.kws[1]}  Embedded args rock here  PASS
    Name and status should be  ${tc.kws[1].kws[0]}  BuiltIn.No Operation  NOT_RUN

Keywords that would fail
    ${tc}=  Check Test Case  ${TESTNAME}
    Should have correct number of keywords  ${tc}  3
    Name and status should be  ${tc.kws[0]}  BuiltIn.Fail  NOT_RUN
    Name and status should be  ${tc.kws[1]}  resource.Fail In UK  PASS
    Should have correct number of keywords  ${tc.kws[1]}  2
    Name and status should be  ${tc.kws[1].kws[0]}  BuiltIn.Fail  NOT_RUN
    Name and status should be  ${tc.kws[1].kws[1]}  BuiltIn.Fail  NOT_RUN

Scalar variables are not checked in keyword arguments
    [Documentation]  Variables are too often set somehow dynamically that we cannot expect them to always exist.
    ${tc}=  Check Test Case  ${TESTNAME}
    Name and status should be  ${tc.kws[0]}  BuiltIn.Log  NOT_RUN
    Name and status should be  ${tc.kws[1]}  BuiltIn.Log  NOT_RUN

List variables are not checked in keyword arguments
    [Documentation]  See the doc of the previous test
    Check Test Case  ${TESTNAME}

Variables are not checked in when arguments are embedded
    [Documentation]  See the doc of the previous test
    ${tc}=  Check Test Case  ${TESTNAME}
    Name and status should be  ${tc.kws[0]}  Embedded \${TESTNAME} here  PASS
    Name and status should be  ${tc.kws[0].kws[0]}  BuiltIn.No Operation  NOT_RUN
    Name and status should be  ${tc.kws[1]}  Embedded \${nonex} here  PASS
    Name and status should be  ${tc.kws[1].kws[0]}  BuiltIn.No Operation  NOT_RUN

User keyword return value
    Check Test Case  ${TESTNAME}

Test Setup and Teardown
    ${tc}=  Check Test Case  ${TESTNAME}
    Should have correct number of keywords  ${tc}  1
    Should Be Equal  ${tc.setup.name}  BuiltIn.Log
    Should Be Equal  ${tc.teardown.name}  Does not exist

Keyword Teardown
    ${tc}=  Check Test Case  ${TESTNAME}
    Should have correct number of keywords  ${tc}  1
    Should Be Equal  ${tc.kws[0].kws[1].name}  Does not exist

For Loops
    ${tc}=  Check Test Case  ${TESTNAME}
    Should have correct number of keywords  ${tc}  3
    Should have correct number of keywords  ${tc.kws[0]}  1
    Should have correct number of keywords  ${tc.kws[0].kws[0]}  2
    Should have correct number of keywords  ${tc.kws[1]}  3
    Should have correct number of keywords  ${tc.kws[1].kws[1]}  1

Non-existing keyword name
    Check Test Case  ${TESTNAME}

Invalid syntax in UK
    Check Test Case  ${TESTNAME}
    Check Log Message  ${ERRORS[1]}  Creating user keyword 'Invalid Syntax UK' failed: Invalid argument '${arg'.  ERROR

Multiple Failures
    Check Test Case  ${TESTNAME}

Invalid imports
    Check Stderr Contains  Importing test library 'DoesNotExist' failed: ImportError: No module named DoesNotExist
    Check Stderr Contains  Variable file 'wrong_path.py' does not exist
    Check Stderr Contains  Resource file 'NonExisting.tsv' does not exist

Test from other suite
    Check Test Case  Some Other Test

*** Keywords ***
Should have correct number of keywords
    [Arguments]  ${test or uk}  ${exp number of kws}
    Log  ${test or uk.kws}
    Should Be Equal As Integers  ${test or uk.kw_count}  ${exp number of kws}

Name and status should be
    [Arguments]  ${kw}  ${name}  ${status}
    Should Be Equal  ${kw.name}    ${name}
    Should Be Equal  ${kw.status}  ${status}
