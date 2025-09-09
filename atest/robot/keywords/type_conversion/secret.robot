*** Settings ***
Resource        atest_resource.robot

Suite Setup     Run Tests    --variable "CLI: Secret:From command line"    keywords/type_conversion/secret.robot


*** Test Cases ***
Command line
    Check Test Case    ${TESTNAME}

Variable section: Based on existing variable
    Check Test Case    ${TESTNAME}

Variable section: Based on environment variable
    Check Test Case    ${TESTNAME}

Variable section: Joined
    Check Test Case    ${TESTNAME}

Variable section: Scalar fail
    Check Test Case    ${TESTNAME}
    Error In File
    ...    6    keywords/type_conversion/secret.robot    11
    ...    Setting variable '\${LITERAL: Secret}' failed:
    ...    Value must have type 'Secret', got string.
    Error In File
    ...    0    keywords/type_conversion/secret.robot    12
    ...    Setting variable '\${BAD: Secret}' failed:
    ...    Value must have type 'Secret', got integer.
    Error In File
    ...    3    keywords/type_conversion/secret.robot    16
    ...    Setting variable '\${JOIN4: Secret}' failed:
    ...    Value must have type 'Secret', got string.

Variable section: List
    Check Test Case    ${TESTNAME}

Variable section: List fail
    Check Test Case    ${TESTNAME}
    Error In File
    ...    4    keywords/type_conversion/secret.robot    19
    ...    Setting variable '\@{LIST3: Secret}' failed:
    ...    Value '['this', Secret(value=<secret>), 'fails']' (list)
    ...    cannot be converted to list[Secret]:
    ...    Item '0' must have type 'Secret', got string.
    ...    pattern=False
    Error In File
    ...    5    keywords/type_conversion/secret.robot    20
    ...    Setting variable '\@{LIST4: Secret}' failed:
    ...    Value '[Secret(value=<secret>), 'this', 'fails', Secret(value=<secret>)]' (list)
    ...    cannot be converted to list[Secret]:
    ...    Item '1' must have type 'Secret', got string.
    ...    pattern=False

Variable section: Dict
    Check Test Case    ${TESTNAME}

Variable section: Dict fail
    Check Test Case    ${TESTNAME}
    Error In File
    ...    1    keywords/type_conversion/secret.robot    24
    ...    Setting variable '\&{DICT4: Secret}' failed:
    ...    Value '{'ok': Secret(value=<secret>), 'this': 'fails'}' (DotDict)
    ...    cannot be converted to dict[Any, Secret]:
    ...    Item 'this' must have type 'Secret', got string.
    ...    pattern=False
    Error In File
    ...    2    keywords/type_conversion/secret.robot    25
    ...    Setting variable '\&{DICT5: str=Secret}' failed:
    ...    Value '{'ok': Secret(value=<secret>), 'var': Secret(value=<secret>),
    ...    'env': Secret(value=<secret>), 'join': Secret(value=<secret>), 'this': 'fails'}' (DotDict)
    ...    cannot be converted to dict[str, Secret]:
    ...    Item 'this' must have type 'Secret', got string.
    ...    pattern=False

VAR: Based on existing variable
    Check Test Case    ${TESTNAME}

VAR: Based on environment variable
    Check Test Case    ${TESTNAME}

VAR: Joined
    Check Test Case    ${TESTNAME}

VAR: Broken variable
    Check Test Case    ${TESTNAME}

VAR: List
    Check Test Case    ${TESTNAME}

Create: Dict
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

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
