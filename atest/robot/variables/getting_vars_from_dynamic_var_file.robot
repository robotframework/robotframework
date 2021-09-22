*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  variables/dynamic_variable_files/getting_vars_from_dynamic_var_file.robot
Resource        atest_resource.robot

*** Test Cases ***
Variables From Dict Should Be Loaded
    Check Test Case  ${TEST NAME}

Variables From My Dict Should Be Loaded
    Check Test Case  ${TEST NAME}

Variables From Mapping Should Be Loaded
    Check Test Case  ${TEST NAME}

Variables From UserDict Should Be Loaded
    Check Test Case  ${TEST NAME}

Variables From My UserDict Should Be Loaded
    Check Test Case  ${TEST NAME}
