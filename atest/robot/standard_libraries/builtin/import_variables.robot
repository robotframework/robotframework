*** Settings ***
Suite Setup     Run Tests  --PYTHONPATH ${DATADIR}/../testresources/res_and_var_files/  standard_libraries/builtin/import_variables.robot
Resource        atest_resource.robot

*** Test Cases ***
Import Variables In Suite Setup
    Check Test Case  ${TEST_NAME}

Import Variables
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2

Import Variables With Arguments
    Check Test Case  ${TESTNAME}

Inport Variables With Invalid Arguments
    Check Test Case  ${TESTNAME}

Import Variables In User Keyword
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2

Re-Import Variables
    Check Test Case  ${TEST_NAME}

Import Variables Arguments Are Resolved Only Once
    Check Test Case  ${TEST NAME}

Import Variables Failure Is Catchable
    Check Test Case  ${TESTNAME}

Import Variables from Path
    Check Test Case  ${TESTNAME}

