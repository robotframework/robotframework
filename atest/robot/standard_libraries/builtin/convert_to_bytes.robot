*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/builtin/convert_to_bytes.robot
Resource         atest_resource.robot

*** Test Cases ***
Default input type is text
    Check Test Case    ${TESTNAME}

Invalid input type fails
    Check Test Case    ${TESTNAME}

ASCII string
    Check Test Case    ${TESTNAME}

Non-ASCII string
    Check Test Case    ${TESTNAME}

Non-ASCII above 255 fails
    Check Test Case    ${TESTNAME}

Characters as a list
    Check Test Case    ${TESTNAME}

Byte string
    Check Test Case    ${TESTNAME}

Bytearray
    Check Test Case    ${TESTNAME}

Integers
    Check Test Case    ${TESTNAME}

Any whitespace as integer separator
    Check Test Case    ${TESTNAME}

Integers with prefixes
    Check Test Case    ${TESTNAME}

Integers as list
    Check Test Case    ${TESTNAME}

Integer as integer
    Check Test Case    ${TESTNAME}

Integers without separators does not work
    Check Test Case    ${TESTNAME}

Too big or small integers
    Check Test Case    ${TESTNAME}

Invalid integers
    Check Test Case    ${TESTNAME}

Hex without whitespace
    Check Test Case    ${TESTNAME}

Hex with whitespace
    Check Test Case    ${TESTNAME}

Hex requires even input
    Check Test Case    ${TESTNAME}

Hex as list
    Check Test Case    ${TESTNAME}

Too big or small hex
    Check Test Case    ${TESTNAME}

Invalid hex
    Check Test Case    ${TESTNAME}

Binary without spaces
    Check Test Case    ${TESTNAME}

Binary with whitespace
    Check Test Case    ${TESTNAME}

Binary requires input to be multiple of 8
    Check Test Case    ${TESTNAME}

Binary as list
    Check Test Case    ${TESTNAME}

Invalid binary
    Check Test Case    ${TESTNAME}

Too big or small binary
    Check Test Case    ${TESTNAME}
