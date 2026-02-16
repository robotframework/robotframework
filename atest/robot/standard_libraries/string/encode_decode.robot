*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/string/encode_decode.robot
Resource         atest_resource.robot

*** Test Cases ***
Encode ASCII String To Bytes
    Check Test Case    ${TESTNAME}

Encode Non-ASCII String To Bytes
    Check Test Case    ${TESTNAME}

Encode Non-ASCII String To Bytes Using Incompatible Encoding
    Check Test Case    ${TESTNAME}

Encode Non-ASCII String To Bytes Using Incompatible Encoding And Error Handler
    Check Test Case    ${TESTNAME}

Encode bytes
    Check Test Case    ${TESTNAME}

Decode ASCII Bytes To String
    Check Test Case    ${TESTNAME}

Decode Non-ASCII Bytes To String
    Check Test Case    ${TESTNAME}

Decode Non-ASCII Bytes To String Using Incompatible Encoding
    Check Test Case    ${TESTNAME}

Decode Non-ASCII Bytes To String Using Incompatible Encoding And Error Handler
    Check Test Case    ${TESTNAME}

Decode string
    Check Test Case    ${TESTNAME}
