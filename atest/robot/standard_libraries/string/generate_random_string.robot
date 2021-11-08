*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/generate_random_string.robot
Resource          atest_resource.robot

*** Test Cases ***
Generate Random String With Defaults
    Check Test Case    ${TESTNAME}

Generate Random String With Empty Length
    Check Test Case    ${TESTNAME}

Generate Random String With Random Length
    Check Test Case    ${TESTNAME}

Generate Random String With Invalid Ranges
    Check Test Case    ${TESTNAME}

Generate Random String From Non Default Characters
    Check Test Case    ${TESTNAME}

Generate Random String From Non Default Characters And [NUMBERS]
    Check Test Case    ${TESTNAME}

Generate Random String With [LOWER]
    Check Test Case    ${TESTNAME}

Generate Random String With [UPPER]
    Check Test Case    ${TESTNAME}

Generate Random String With [LETTERS]
    Check Test Case    ${TESTNAME}

Generate Random String With [NUMBERS]
    Check Test Case    ${TESTNAME}

