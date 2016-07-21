*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    variables/variables_from_variable_files.robot
Resource          atest_resource.robot

*** Test Case ***
Scalar String
    Check Test Case    ${TEST NAME}

Scalar Non-Strings
    Check Test Case    ${TEST NAME}

Scalar String With Escapes
    Check Test Case    ${TEST NAME}

Empty Scalar String
    Check Test Case    ${TEST NAME}

Scalar List
    Check Test Case    ${TEST NAME}

Scalar List With Non-Strings
    Check Test Case    ${TEST NAME}

Scalar List With Escapes
    Check Test Case    ${TEST NAME}

Scalar Object
    Check Test Case    ${TEST NAME}

List with One Item
    Check Test Case    ${TEST NAME}

List With Multiple Items
    Check Test Case    ${TEST NAME}

List With Escapes
    Check Test Case    ${TEST NAME}

List With No Items
    Check Test Case    ${TEST NAME}

List With Objects
    Check Test Case    ${TEST NAME}

Variable Names Are Case Insensitive
    Check Test Case    ${TEST NAME}

Variable Names Are Underscore Insensitive
    Check Test Case    ${TEST NAME}

Variables From Variable Files Can Be Used In Local Variable Table
    Check Test Case    ${TEST NAME}
