*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/string.robot
Resource          atest_resource.robot

*** Test Cases ***
Fetch From Left
    Check Test Case    ${TESTNAME}

Fetch From Left with bytes
    Check Test Case    ${TESTNAME}

Fetch From Right
    Check Test Case    ${TESTNAME}

Fetch From Right with bytes
    Check Test Case    ${TESTNAME}

Get Line
    Check Test Case    ${TESTNAME}

Get Line with bytes
    Check Test Case    ${TESTNAME}

Get Line Count
    Check Test Case    ${TESTNAME}

Get Line Count with bytes
    Check Test Case    ${TESTNAME}

Split To Lines
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    2 lines returned.
    Check Log Message    ${tc[4, 0]}    1 line returned.
    Check Log Message    ${tc[7, 0]}    0 lines returned.

Split To Lines With Start Only
    Check Test Case    ${TESTNAME}

Split To Lines With Start And End
    Check Test Case    ${TESTNAME}

Split To Lines With End Only
    Check Test Case    ${TESTNAME}

Split To Lines with empty string as start index is deprecated
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}     Using an empty string as a value with argument 'start' is deprecated. Use '0' instead.    WARN

Split To Lines With Negative Values
    Check Test Case    ${TESTNAME}

Split To Lines With Invalid Start
    Check Test Case    ${TESTNAME}

Split To Lines With Invalid End
    Check Test Case    ${TESTNAME}

Split To Lines with bytes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    5 lines returned.

Get Substring
    Check Test Case    ${TESTNAME}

Get Substring With Negative Values
    Check Test Case    ${TESTNAME}

Get Substring With Start Only
    Check Test Case    ${TESTNAME}

Get Substring with end only
    Check Test Case    ${TESTNAME}

Get Substring with empty string as start index is deprecated
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}     Using an empty string as a value with argument 'start' is deprecated. Use '0' instead.    WARN

Get Substring With Invalid Start
    Check Test Case    ${TESTNAME}

Get Substring With Invalid End
    Check Test Case    ${TESTNAME}

Get Substring with bytes
    Check Test Case    ${TESTNAME}

Strip String
    Check Test Case    ${TESTNAME}

Strip String Left
    Check Test Case    ${TESTNAME}

Strip String Right
    Check Test Case    ${TESTNAME}

Strip String None
    Check Test Case    ${TESTNAME}

Strip String With Invalid Mode
    Check Test Case    ${TESTNAME}

Strip String With Given Characters
    Check Test Case    ${TESTNAME}

Strip String With Given Characters none
    Check Test Case    ${TESTNAME}

Strip String with bytes
    Check Test Case    ${TESTNAME}
