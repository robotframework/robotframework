*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/generate_random_string.robot
Resource          atest_resource.robot

*** Test Cases ***
Generate Random String With Defaults
    Check Test Case    ${TESTNAME}

Generate Random String with empty string as length is deprecated
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}     Using an empty string as a value with argument 'length' is deprecated. Use '8' instead.    WARN

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

Generate Random String With [ARABIC]
    Check Test Case    ${TESTNAME}

Generate Random String With [POLISH]
    Check Test Case    ${TESTNAME}
