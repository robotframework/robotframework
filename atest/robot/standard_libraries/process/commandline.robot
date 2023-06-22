*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/commandline.robot
Resource         atest_resource.robot

*** Test Cases ***
Split command line basics
    Check Test Case    ${TESTNAME}

Split command line with internal quotes
    Check Test Case    ${TESTNAME}

Split command line with unbalanced quotes
    Check Test Case    ${TESTNAME}

Split command line with escaping
    Check Test Case    ${TESTNAME}

Split command line with pathlib.Path
    Check Test Case    ${TESTNAME}

Join command line basics
    Check Test Case    ${TESTNAME}

Join command line with internal quotes
    Check Test Case    ${TESTNAME}

Join command line with escaping
    Check Test Case    ${TESTNAME}

Join command line with non-strings
    Check Test Case    ${TESTNAME}
