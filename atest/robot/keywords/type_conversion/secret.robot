*** Settings ***
Resource        atest_resource.robot

Suite Setup     Run Tests    --variable "CLI: Secret:From command line"    keywords/type_conversion/secret.robot


*** Test Cases ***
Command line
    Check Test Case    ${TESTNAME}

Variable section: Scalar
    Check Test Case    ${TESTNAME}

Variable section: List
    Check Test Case    ${TESTNAME}

Variable section: Dict
    Check Test Case    ${TESTNAME}

Variable section: Invalid syntax
    Error In File
    ...    0    keywords/type_conversion/secret.robot    18
    ...    Setting variable '\&{DICT_LITERAL: secret}' failed:
    ...    Value 'fails' must have type 'Secret', got string.
    Error In File
    ...    1    keywords/type_conversion/secret.robot    9
    ...    Setting variable '\${FROM_LITERAL: Secret}' failed:
    ...    Value 'this fails' must have type 'Secret', got string.
    Error In File
    ...    2    keywords/type_conversion/secret.robot    15
    ...    Setting variable '\@{LIST_LITERAL: secret}' failed:
    ...    Value 'this' must have type 'Secret', got string.

VAR: Env variable
    Check Test Case    ${TESTNAME}

VAR: Join secret
    Check Test Case    ${TESTNAME}

VAR: Broken variable
    Check Test Case    ${TESTNAME}

Create: List
    Check Test Case    ${TESTNAME}

Create: List by extending
    Check Test Case    ${TESTNAME}

Create: List of dictionaries
    Check Test Case    ${TESTNAME}

Create: Dictionary
    Check Test Case    ${TESTNAME}

Return value: Library keyword
    Check Test Case    ${TESTNAME}

Return value: User keyword
    Check Test Case    ${TESTNAME}

User keyword: Receive not secret
    Check Test Case    ${TESTNAME}

User keyword: Receive not secret var
    Check Test Case    ${TESTNAME}

Library keyword
    Check Test Case    ${TESTNAME}

Library keyword: not secret
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Library keyword: TypedDict
    Check Test Case    ${TESTNAME}

Library keyword: List of secrets
    Check Test Case    ${TESTNAME}
