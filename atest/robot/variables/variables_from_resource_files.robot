*** Settings ***
Suite Setup       Run tests    ${EMPTY}    variables/variables_from_resource_files.robot
Resource          atest_resource.robot

*** Test Cases ***
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

List with One Item
    Check Test Case    ${TEST NAME}

List With Multiple Items
    Check Test Case    ${TEST NAME}

List With Escapes
    Check Test Case    ${TEST NAME}

List Created From List With Escapes
    Check Test Case    ${TEST NAME}

List With No Items
    Check Test Case    ${TEST NAME}

Variable Names Are Case Insensitive
    Check Test Case    ${TEST NAME}

Variable Names Are Space Insensitive
    Check Test Case    ${TEST NAME}

Variable Names Are Underscore Insensitive
    Check Test Case    ${TEST NAME}

Assign Mark With Scalar variable
    Check Test Case    ${TEST NAME}

Assign Mark With List variable
    Check Test Case    ${TEST NAME}

Variables From Resource Files Can Be Used In Local Variable Table
    Check Test Case    ${TEST NAME}

Imported Resource Can Use Variables From Resources It Imports In Its Variable Table
    Check Test Case    ${TEST NAME}
