*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  variables/variables_inside_variables.robot
Resource        atest_resource.robot

*** Test Cases ***
Variable Inside Variable In Variable Table
    Check Test Case  ${TEST NAME}

Variable Inside Variable In Test Case
    Check Test Case  ${TEST NAME}

Variable Inside Variable In User Keyword
    Check Test Case  ${TEST NAME}

Variable Inside List Variables
    Check Test Case  ${TEST NAME}

Variable Inside Dict Variables
    Check Test Case  ${TEST NAME}

Variable Inside Variable Item
    Check Test Case  ${TEST NAME}

Variable Inside Variable And Extended Variable Syntax
    Check Test Case  ${TEST NAME}

Non-Existing Variable Inside Variable
    Check Test Case  ${TEST NAME}
