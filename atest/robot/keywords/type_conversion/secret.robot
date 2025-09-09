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
    ...    0    keywords/type_conversion/secret.robot    28
    ...    Setting variable '\&{DICT3: Secret}' failed:
    ...    Value '{'a': 'b'}' (DotDict) cannot be converted to dict[Any, Secret]:
    ...    Item 'a' must have type 'Secret', got string.
    ...    pattern=${False}
    Error In File
    ...    1    keywords/type_conversion/secret.robot    26
    ...    Setting variable '\&{DICT_LITERAL: secret}' failed:
    ...    Value 'fails' must have type 'Secret', got string.
    Error In File
    ...    2    keywords/type_conversion/secret.robot    9
    ...    Setting variable '\${FROM_LITERAL: Secret}' failed:
    ...    Value 'this fails' must have type 'Secret', got string.
    Error In File
    ...    3    keywords/type_conversion/secret.robot    22
    ...    Setting variable '\@{LIST2: Secret}' failed:
    ...    Value '\@{LIST_NORMAL}' must have type 'Secret', got string.
    Error In File
    ...    4    keywords/type_conversion/secret.robot    23
    ...    Setting variable '\@{LIST3: Secret}' failed:
    ...    Value '\@{LIST}' must have type 'Secret', got string.
    Error In File
    ...    5    keywords/type_conversion/secret.robot    20
    ...    Setting variable '\@{LIST_LITERAL: secret}' failed:
    ...    Value 'this' must have type 'Secret', got string.
    Error In File
    ...    6    keywords/type_conversion/secret.robot    14
    ...    Setting variable '\${NO_VAR: secret}' failed:
    ...    Value '=\${42}=' must have type 'Secret', got string.

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
