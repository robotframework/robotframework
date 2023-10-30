*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    variables/dynamic_variable_files/getting_vars_from_dynamic_var_file.robot
Resource        atest_resource.robot

*** Test Cases ***
Variables From Dict Should Be Loaded
    Check Test Case    ${TEST NAME}

Variables From My Dict Should Be Loaded
    Check Test Case    ${TEST NAME}

Variables From Mapping Should Be Loaded
    Check Test Case    ${TEST NAME}

Variables From UserDict Should Be Loaded
    Check Test Case    ${TEST NAME}

Variables From My UserDict Should Be Loaded
    Check Test Case    ${TEST NAME}

Argument conversion
    Check Test Case    ${TEST NAME}

Failing argument conversion
    ${path} =    Normalize Path    ${DATADIR}/variables/dynamic_variable_files/argument_conversion.py
    Error In File    0    variables/dynamic_variable_files/getting_vars_from_dynamic_var_file.robot    8
    ...    Processing variable file '${path}' with arguments ['ok', 'bad'] failed:
    ...    ValueError: Argument 'number' got value 'bad' that cannot be converted to integer or float.
    ...    pattern=False
