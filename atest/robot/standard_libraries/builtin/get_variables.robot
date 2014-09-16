*** Settings ***
Force Tags  regression  pybot  jybot
Suite Setup  Run Tests  --variable cmd_line:cmd_value  standard_libraries/builtin/get_variables.robot
Resource    atest_resource.robot

*** Test Cases ***
Automatic and Command Line Variables
    Check test Case  ${TEST NAME}

Variable Table
    Check test Case  ${TEST NAME}

Global Variables
    Check test Case  ${TEST NAME}

Suite Variables
    Check test Case  ${TEST NAME}
    Check test Case  ${TEST NAME} 2

Resource File
    Check test Case  ${TEST NAME}

Variable File
    Check test Case  ${TEST NAME}

Test Case Variable
    Check test Case  ${TEST NAME}

Set Variable in User Keyword
    Check test Case  ${TEST NAME}

Local Variables in Test Case Leak
    Check test Case  ${TEST NAME}

Variables Are Returned as NormalizedDict
    Check test Case  ${TEST NAME}

Modifying Returned Variables Has No Effect On Real Variables
    Check test Case  ${TEST NAME}
