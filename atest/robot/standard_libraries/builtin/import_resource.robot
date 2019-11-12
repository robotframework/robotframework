*** Settings ***
Suite Setup     Run Tests
...    --variable WINDOWS:${INTERPRETER.is_windows} --PYTHONPATH ${DATADIR}/../testresources/res_and_var_files/
...    standard_libraries/builtin/import_resource.robot
Resource        atest_resource.robot

*** Test Cases ***

Import Resource In Suite Setup
    Check Test Case  ${TESTNAME}

Import Resource With Sub Resources
    Check Test Case  ${TESTNAME}

Import Resource In Test Case
    Check Test Case  ${TESTNAME}

Import Resource In User Keyword
    Check Test Case  ${TESTNAME}

Variables And Keywords Imported In Test Are Available In Next
    Check Test Case  ${TESTNAME}

Re-Import Resource
    Check Test Case  ${TESTNAME}

Import Resource Failure Is Catchable
    Check Test Case  ${TESTNAME}

Import Resource From Pythonpath
    Check Test Case  ${TESTNAME}
