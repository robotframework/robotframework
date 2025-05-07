*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    variables/variable_types.robot
Resource          atest_resource.robot

*** Test Cases ***
Variable section
    Check Test Case    ${TESTNAME}

Variable section: List
    Check Test Case    ${TESTNAME}

Variable section: Dictionary
    Check Test Case    ${TESTNAME}

Variable section: With invalid values or types
    Check Test Case    ${TESTNAME}

Variable section: Invalid syntax
    Error In File
    ...    3    variables/variable_types.robot
    ...    18    Setting variable '\${BAD_TYPE: hahaa}' failed: Unrecognized type 'hahaa'.
    Error In File
    ...    4    variables/variable_types.robot    20
    ...    Setting variable '\@{BAD_LIST_TYPE: xxxxx}' failed: Unrecognized type 'xxxxx'.
    Error In File
    ...    5    variables/variable_types.robot    22
    ...    Setting variable '\&{BAD_DICT_TYPE: aa=bb}' failed: Unrecognized type 'aa'.
    Error In File
    ...    6    variables/variable_types.robot    23
    ...    Setting variable '\&{INVALID_DICT_TYPE1: int=list[int}' failed:
    ...    Parsing type 'dict[int, list[int]' failed:
    ...    Error at end: Closing ']' missing.
    ...    pattern=False
    Error In File
    ...    7    variables/variable_types.robot    24
    ...    Setting variable '\&{INVALID_DICT_TYPE2: int=listint]}' failed:
    ...    Parsing type 'dict[int, listint]]' failed:
    ...    Error at index 18: Extra content after 'dict[int, listint]'.
    ...    pattern=False
    Error In File
    ...    9    variables/variable_types.robot    21
    ...    Setting variable '\&{BAD_DICT_VALUE: str=int}' failed:
    ...    Value '{'x': 'a', 'y': 'b'}' (DotDict) cannot be converted to dict[str, int]:
    ...    Item 'x' got value 'a' that cannot be converted to integer.
    ...    pattern=False
    Error In File
    ...    10    variables/variable_types.robot    19
    ...    Setting variable '\@{BAD_LIST_VALUE: int}' failed:
    ...    Value '['1', 'hahaa']' (list) cannot be converted to list[int]:
    ...    Item '1' got value 'hahaa' that cannot be converted to integer.
    ...    pattern=False
    Error In File
    ...    11    variables/variable_types.robot    17
    ...    Setting variable '\${BAD_VALUE: int}' failed: Value 'not int' cannot be converted to integer.
    ...    pattern=False

VAR syntax
    Check Test Case    ${TESTNAME}

VAR syntax: List
    Check Test Case    ${TESTNAME}

VAR syntax: Dictionary
    Check Test Case    ${TESTNAME}

VAR syntax: Invalid scalar value
    Check Test Case    ${TESTNAME}

VAR syntax: Invalid scalar type
    Check Test Case    ${TESTNAME}

VAR syntax: Type can not be set as variable
    Check Test Case    ${TESTNAME}

VAR syntax: Type syntax is not resolved from variable
    Check Test Case    ${TESTNAME}

Variable assignment
    Check Test Case    ${TESTNAME}

Variable assignment: List
    Check Test Case    ${TESTNAME}

Variable assignment: Dictionary
    Check Test Case    ${TESTNAME}

Variable assignment: Invalid value
    Check Test Case    ${TESTNAME}

Variable assignment: Invalid type
    Check Test Case    ${TESTNAME}

Variable assignment: Invalid variable type for list
    Check Test Case    ${TESTNAME}

Variable assignment: Invalid type for list
    Check Test Case    ${TESTNAME}

Variable assignment: Invalid variable type for dictionary
    Check Test Case    ${TESTNAME}

Variable assignment: No type when using variable
    Check Test Case    ${TESTNAME}

Variable assignment: Multiple
    Check Test Case    ${TESTNAME}

Variable assignment: Multiple list and scalars
    Check Test Case    ${TESTNAME}

Variable assignment: Invalid type for list in multiple variable assignment
    Check Test Case    ${TESTNAME}

Variable assignment: Type can not be set as variable
    Check Test Case    ${TESTNAME}

Variable assignment: Type syntax is not resolved from variable
    Check Test Case    ${TESTNAME}

Variable assignment: Extended
    Check Test Case    ${TESTNAME}

Variable assignment: Item
    Check Test Case    ${TESTNAME}

User keyword
    Check Test Case    ${TESTNAME}

User keyword: Default value
    Check Test Case    ${TESTNAME}

User keyword: Wrong default value
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

User keyword: Invalid value
    Check Test Case    ${TESTNAME}

User keyword: Invalid type
    Check Test Case    ${TESTNAME}
    Error In File
    ...    0    variables/variable_types.robot    355
    ...    Creating keyword 'Bad type' failed:
    ...    Invalid argument specification: Invalid argument '\${arg: bad}':
    ...    Unrecognized type 'bad'.

User keyword: Invalid assignment with kwargs k_type=v_type declaration
    Check Test Case    ${TESTNAME}
    Error In File
    ...    1    variables/variable_types.robot    359
    ...    Creating keyword 'Kwargs does not support key=value type syntax' failed:
    ...    Invalid argument specification: Invalid argument '\&{kwargs: int=float}':
    ...    Unrecognized type 'int=float'.

Embedded arguments
    Check Test Case    ${TESTNAME}

Embedded arguments: With variables
    Check Test Case    ${TESTNAME}

Embedded arguments: Invalid type in library
    Check Test Case    ${TESTNAME}
    Error in library
    ...    Embedded
    ...    Adding keyword 'bad_type' failed:
    ...    Invalid embedded argument '\${value: bad}': Unrecognized type 'bad'.
    ...    index=8

Embedded arguments: Type only in embedded
    Check Test Case    ${TESTNAME}

Embedded arguments: Invalid value
    Check Test Case    ${TESTNAME}

Embedded arguments: Invalid value from variable
    Check Test Case    ${TESTNAME}

Embedded arguments: Invalid type
    Check Test Case    ${TESTNAME}
    Error In File
    ...    2    variables/variable_types.robot    379
    ...    Creating keyword 'Embedded invalid type \${x: invalid}' failed:
    ...    Invalid embedded argument '\${x: invalid}':
    ...    Unrecognized type 'invalid'.

Variable usage does not support type syntax
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Set global/suite/test/local variable: No support
    Check Test Case    ${TESTNAME}
