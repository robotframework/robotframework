*** Settings ***
Suite Setup       Run Tests    sources=standard_libraries/builtin/should_xxx_with.robot
Resource          builtin_resource.robot

*** Test Cases ***
Should Start With
    Check test case    ${TESTNAME}

Should Start With without values
    Check test case    ${TESTNAME}

Should Start With case-insensitive
    Check test case    ${TESTNAME}

Should Start With without leading spaces
    Check test case    ${TESTNAME}

Should Start With without trailing spaces
    Check test case    ${TESTNAME}

Should Start With without leading and trailing spaces
    Check test case    ${TESTNAME}

Should Start With and do not collapse spaces
    Check test case    ${TESTNAME}

Should Start With and collapse spaces
    Check test case    ${TESTNAME}

Should Start With with bytes normalization
    Check test case    ${TESTNAME}

Should Start With with bytes auto conversion
    Check test case    ${TESTNAME}

Should Not Start With
    Check test case    ${TESTNAME}

Should Not Start With without values
    Check test case    ${TESTNAME}

Should Not Start With case-insensitive
    Check test case    ${TESTNAME}

Should Not Start With without leading spaces
    Check test case    ${TESTNAME}

Should Not Start With without trailing spaces
    Check test case    ${TESTNAME}

Should Not Start With without leading and trailing spaces
    Check test case    ${TESTNAME}

Should Not Start With and do not collapse spaces
    Check test case    ${TESTNAME}

Should Not Start With and collapse spaces
    Check test case    ${TESTNAME}

Should Not Start With with bytes normalization
    Check test case    ${TESTNAME}

Should Not Start With with bytes conversion
    Check test case    ${TESTNAME}

Should End With
    Check test case    ${TESTNAME}

Should End With without values
    Check test case    ${TESTNAME}

Should End With case-insensitive
    Check test case    ${TESTNAME}

Should End With without leading spaces
    Check test case    ${TESTNAME}

Should End With without trailing spaces
    Check test case    ${TESTNAME}

Should End With without leading and trailing spaces
    Check test case    ${TESTNAME}

Should End With and do not collapse spaces
    Check test case    ${TESTNAME}

Should End With and collapse spaces
    Check test case    ${TESTNAME}

Should End With with bytes normalization
    Check test case    ${TESTNAME}

Should End With with bytes auto conversion
    Check test case    ${TESTNAME}

Should Not End With
    Check test case    ${TESTNAME}

Should Not End With case-insensitive
    Check test case    ${TESTNAME}

Should Not End With without leading spaces
    Check test case    ${TESTNAME}

Should Not End With without trailing spaces
    Check test case    ${TESTNAME}

Should Not End With without leading and trailing spaces
    Check test case    ${TESTNAME}

Should Not End With and do not collapse spaces
    Check test case    ${TESTNAME}

Should Not End With and collapse spaces
    Check test case    ${TESTNAME}

Should Not End With with bytes normalization
    Check test case    ${TESTNAME}

Should Not End With with bytes conversion
    Check test case    ${TESTNAME}

NO VALUES is deprecated
    ${tc} =    Check test case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}   Using 'NO VALUES' for disabling the 'values' argument is deprecated. Use 'values=False' instead.    WARN
    Check Log Message    ${tc[1, 0]}   Using 'no values' for disabling the 'values' argument is deprecated. Use 'values=False' instead.    WARN
    Check Log Message    ${tc[2, 0]}   Using 'No values' for disabling the 'values' argument is deprecated. Use 'values=False' instead.    WARN
    Check Log Message    ${tc[3, 0]}   Using 'No Values' for disabling the 'values' argument is deprecated. Use 'values=False' instead.    WARN
