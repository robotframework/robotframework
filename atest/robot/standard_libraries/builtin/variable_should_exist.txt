*** Settings ***
Documentation   Tests for variable should and should not exist related functionality in BuiltIn
Suite Setup     Run Tests  ${EMPTY}  standard_libraries${/}builtin${/}variable_should_exist.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***
Variable Should Exist With Default Error Message
    Check Test Case  Variable Should Exist With Default Error Message

Variable Should Exist With Given Error Message
    Check Test Case  Variable Should Exist With Given Error Message

Variable Should Exist With Error Message Containing Variables
    Check Test Case  Variable Should Exist With Error Message Containing Variables

Variable Should Exist Using $name format
    Check Test Case  Variable Should Exist Using $name format

Variable Should Exist Using Escaped format
    Check Test Case  Variable Should Exist Using Escaped format

Variable Should Exist With Built In Variables
    Check Test Case  Variable Should Exist With Built In Variables

Variable Should Exist With Extended Variable Syntax
    Check Test Case  Variable Should Exist With Extended Variable Syntax

Variable Should Exist With Extended Variable Syntax And Missing Object
    Check Test Case  Variable Should Exist With Extended Variable Syntax And Missing Object

Variable Should Exist With Invalid name
    Check Test Case  Variable Should Exist With Invalid name

Variable Should Not Exist With Default error message
    Check Test Case  Variable Should Not Exist With Default error message

Variable Should Not Exist With Given Error Message
    Check Test Case  Variable Should Not Exist With Given Error Message

Variable Should Not Exist With Error Message Containing Variables
    Check Test Case  Variable Should Not Exist With Error Message Containing Variables

Variable Should Not Exist Using $name format
    Check Test Case  Variable Should Not Exist Using $name format

Variable Should Not Exist Using Escaped format
    Check Test Case  Variable Should Not Exist Using Escaped Format

Variable Should Not Exist With Built In Variables
    Check Test Case  Variable Should Not Exist With Built In Variables

Variable Should Not Exist With Extended Variable Syntax
    Check Test Case  Variable Should Not Exist With Extended Variable Syntax

Variable Should Not Exist With Extended Variable Syntax And Missing Object
    Check Test Case  Variable Should Not Exist With Extended Variable Syntax And Missing Object

Variable Should Not Exist With Invalid name
    Check Test Case  Variable Should Not Exist With Invalid name

Variable Should Exist In User Keyword When Variable Name Is Argument And Variable Exists
    Check Test Case  ${TEST NAME}

Variable Should Exist In User Keyword Fails When Variable Name Is Argument And Variable Does Not Exists
    Check Test Case  ${TEST NAME}

Variable Should Not Exists In User Keyword When Variable Name Is Argument
    Check Test Case  ${TEST NAME}

Variable Should Exist When Variable Has Variable Like Value
    Check Test Case  ${TEST NAME}

Variable Should Not Exist Fails When Variable Has Variable Like Value
    Check Test Case  ${TEST NAME}

