*** Settings ***
Documentation     Tests for variable should and should not exist related functionality in BuiltIn
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/variable_should_exist.robot
Resource          atest_resource.robot

*** Test Cases ***
Variable Should Exist With Default Error Message
    Check Test Case    ${TEST NAME}

Variable Should Exist With Given Error Message
    Check Test Case    ${TEST NAME}

Variable Should Exist With Error Message Containing Variables
    Check Test Case    ${TEST NAME}

Variable Should Exist Using $name format
    Check Test Case    ${TEST NAME}

Variable Should Exist Using Escaped format
    Check Test Case    ${TEST NAME}

Variable Should Exist With Variables
    Check Test Case    ${TEST NAME}

Variable Should Exist With Built In Variables
    Check Test Case    ${TEST NAME}

Variable Should Exist With Extended Variable Syntax
    Check Test Case    ${TEST NAME}

Variable Should Exist With Extended Variable Syntax And Missing Object
    Check Test Case    ${TEST NAME}

Variable Should Exist With Invalid name
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Variable Should Not Exist With Default error message
    Check Test Case    ${TEST NAME}

Variable Should Not Exist With Given Error Message
    Check Test Case    ${TEST NAME}

Variable Should Not Exist With Error Message Containing Variables
    Check Test Case    ${TEST NAME}

Variable Should Not Exist Using $name format
    Check Test Case    ${TEST NAME}

Variable Should Not Exist Using Escaped format
    Check Test Case    ${TEST NAME}

Variable Should Not Exist With Variables
    Check Test Case    ${TEST NAME}

Variable Should Not Exist With Built In Variables
    Check Test Case    ${TEST NAME}

Variable Should Not Exist With Extended Variable Syntax
    Check Test Case    ${TEST NAME}

Variable Should Not Exist With Extended Variable Syntax And Missing Object
    Check Test Case    ${TEST NAME}

Variable Should Not Exist With Invalid name
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Variable Should Exist In User Keyword When Variable Name Is Argument And Variable Exists
    Check Test Case    ${TEST NAME}

Variable Should Exist In User Keyword Fails When Variable Name Is Argument And Variable Does Not Exists
    Check Test Case    ${TEST NAME}

Variable Should Not Exists In User Keyword When Variable Name Is Argument
    Check Test Case    ${TEST NAME}

Variable Should Exist When Variable Has Variable Like Value
    Check Test Case    ${TEST NAME}

Variable Should Not Exist Fails When Variable Has Variable Like Value
    Check Test Case    ${TEST NAME}
