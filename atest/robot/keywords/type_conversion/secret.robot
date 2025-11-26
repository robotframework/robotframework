*** Settings ***
Resource        atest_resource.robot
Suite Setup     Run Tests    --variable "CLI: Secret:From command line" -L trace    keywords/type_conversion/secret.robot

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
    ...    3    keywords/type_conversion/secret.robot    20
    ...    Setting variable '\${JOIN4: Secret}' failed:
    ...    Value must have type 'Secret', got string.
    Error In File
    ...    7    keywords/type_conversion/secret.robot    14
    ...    Setting variable '\${SECRET_BOOL: bool}' failed:
    ...    Value '<secret>' (Secret) cannot be converted to boolean.
    Error In File
    ...    8    keywords/type_conversion/secret.robot    13
    ...    Setting variable '\${SECRET_STR: str}' failed:
    ...    Value '<secret>' (Secret) cannot be converted to string.

Variable section: List
    Check Test Case    ${TESTNAME}

Variable section: List fail
    Check Test Case    ${TESTNAME}
    Error In File
    ...    4    keywords/type_conversion/secret.robot    23
    ...    Setting variable '\@{LIST3: Secret}' failed:
    ...    Value '['this', Secret(value=<secret>), 'fails']' (list)
    ...    cannot be converted to list[Secret]:
    ...    Item '0' must have type 'Secret', got string.
    ...    pattern=False
    Error In File
    ...    5    keywords/type_conversion/secret.robot    24
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
    ...    1    keywords/type_conversion/secret.robot    28
    ...    Setting variable '\&{DICT4: Secret}' failed:
    ...    Value '{'ok': Secret(value=<secret>), 'this': 'fails'}' (DotDict)
    ...    cannot be converted to dict[Any, Secret]:
    ...    Item 'this' must have type 'Secret', got string.
    ...    pattern=False
    Error In File
    ...    2    keywords/type_conversion/secret.robot    29
    ...    Setting variable '\&{DICT5: str=Secret}' failed:
    ...    Value '{'ok': Secret(value=<secret>), 'var': Secret(value=<secret>),
    ...    'env': Secret(value=<secret>), 'join': Secret(value=<secret>), 'this': 'fails'}' (DotDict)
    ...    cannot be converted to dict[str, Secret]:
    ...    Item 'this' must have type 'Secret', got string.
    ...    pattern=False

VAR: Based on existing variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    \${x} = <secret>

VAR: Based on environment variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}    \${secret} = <secret>

VAR: Joined
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[2, 0]}    \${x} = <secret>

VAR: Broken variable
    Check Test Case    ${TESTNAME}

VAR: List
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    \@{x} = [ <secret> | <secret> | <secret> ]

VAR: Dict
    ${tc} =    Check Test Case    ${TESTNAME} 1
    Check Log Message    ${tc[0, 0]}    \&{x} = { var=<secret> | end=<secret> | join=<secret> }
    Check Test Case    ${TESTNAME} 2

Return value: User keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, -2]}    Return: Secret(value=<secret>)    TRACE
    Check Log Message    ${tc[0, -1]}    \${x} = <secret>

Return value: Library keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, -2]}    Return: Secret(value=<secret>)    TRACE
    Check Log Message    ${tc[0, -1]}    \${x} = <secret>

Arguments: User keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Arguments: [ \${secret}=Secret(value=<secret>) | \${expected}='Secret value' ]    TRACE

Arguments: User keyword non-secret
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Arguments: User keyword fail str
    Check Test Case    ${TESTNAME}

Arguments: User keyword fail bool
    Check Test Case    ${TESTNAME}

Arguments: User keyword Any
    Check Test Case    ${TESTNAME}

Arguments: User keyword object
    Check Test Case    ${TESTNAME}

Arguments: Library keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Arguments: [ Secret(value=<secret>) ]    TRACE

Arguments: Library keyword non-secret
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Arguments: Library keyword fail str
    Check Test Case    ${TESTNAME}

Arguments: Library keyword fail bool
    Check Test Case    ${TESTNAME}

Arguments: Library keyword fail list str
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Arguments: Library keyword any
    Check Test Case    ${TESTNAME}

Arguments: Library keyword object
    Check Test Case    ${TESTNAME}

Arguments: List of secrets
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}    Arguments: [ [Secret(value=<secret>), Secret(value=<secret>)] ]    TRACE

Arguments: TypedDict
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}    Arguments: [ {'username': 'login@email.com', 'password': Secret(value=<secret>)} ]    TRACE
