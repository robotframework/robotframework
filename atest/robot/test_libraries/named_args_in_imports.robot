*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/named_args_in_imports.robot
Resource        atest_resource.robot

*** Test Cases ***
Check kw arguments
    Check Test Case  ${TESTNAME}

Normal Named Arguments
    Check Test Case  ${TESTNAME}

Non String Value
    Check Test Case  ${TESTNAME}

Named Argument Syntax Doesn't Work Inside Variable
    Check Test Case  ${TESTNAME}

WITH NAME Doesn't Work Inside Variable
    Check Test Case  ${TESTNAME}

