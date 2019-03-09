*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    running/test_named_arguments.robot
Resource          atest_resource.robot

*** Test Cases ***
Test Named Arguments with only one named argument
    check test case  ${TESTNAME}

Test Named Arguments with only one named argument but we have a escaped egal
    check test case  ${TESTNAME}

Test Named Arguments with only one named argument but we have a no escaped egal
    check test case  ${TESTNAME}

Test Named Arguments with only one named argument but we have two no escaped egal
    check test case  ${TESTNAME}

Test Named Arguments with two named argument but with a error
    check test case  ${TESTNAME}    FAIL    Keyword 'Named Arg Test' got positional argument after named arguments.

