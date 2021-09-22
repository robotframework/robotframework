*** Settings ***
Suite Setup      Run Remote Tests    argument_coersion.robot    arguments.py
Resource         remote_resource.robot

*** Test Cases ***
String
    Check Test Case    ${TESTNAME}

Newline and tab
    Check Test Case    ${TESTNAME}

Binary
    Check Test Case    ${TESTNAME}

Binary in non-ASCII range
    Check Test Case    ${TESTNAME}

Binary with too big Unicode characters
    Check Test Case    ${TESTNAME}

Unrepresentable Unicode
    Check Test Case    ${TESTNAME}

Integer
    Check Test Case    ${TESTNAME}

Float
    Check Test Case    ${TESTNAME}

Boolean
    Check Test Case    ${TESTNAME}

None
    Check Test Case    ${TESTNAME}

Custom object
    Check Test Case    ${TESTNAME}

Custom object with non-ASCII representation
    Check Test Case    ${TESTNAME}

Custom object with binary representation
    Check Test Case    ${TESTNAME}

List
    Check Test Case    ${TESTNAME}

List with non-string values
    Check Test Case    ${TESTNAME}

List with non-ASCII values
    Check Test Case    ${TESTNAME}

List with non-ASCII byte values
    Check Test Case    ${TESTNAME}

List with binary values
    Check Test Case    ${TESTNAME}

Nested list
    Check Test Case    ${TESTNAME}

List-like
    Check Test Case    ${TESTNAME}

Dictionary
    Check Test Case    ${TESTNAME}

Dictionary with non-string keys and values
    Check Test Case    ${TESTNAME}

Dictionary with non-ASCII keys
    Check Test Case    ${TESTNAME}

Dictionary with non-ASCII values
    Check Test Case    ${TESTNAME}

Dictionary with non-ASCII byte keys
    Check Test Case    ${TESTNAME}

Dictionary with non-ASCII byte values
    Check Test Case    ${TESTNAME}

Dictionary with binary keys is not supported
    Check Test Case    ${TESTNAME}

Dictionary with binary values
    Check Test Case    ${TESTNAME}

Nested dictionary
    Check Test Case    ${TESTNAME}

Mapping
    Check Test Case    ${TESTNAME}
