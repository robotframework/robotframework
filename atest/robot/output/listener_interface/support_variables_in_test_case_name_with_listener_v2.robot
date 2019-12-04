*** Settings ***
Suite Setup      Run Tests    --listener ${DATADIR}/output/listeners/verify_var_name_in_test_case_v2.py    output/listeners/support_variables_in_test_case_name.robot
Resource         atest_resource.robot


*** Variables ***
${MESSAGE FILE}    %{TEMPDIR}${/}messages.txt

*** Test Cases ***
Test Case Name With Variable
    Check Test Case    Test Case \${NAME} With \${VARIABLE}
    Check Stdout Contains    SEPARATOR=\n
    ...    [Start] [name] Test Case \${NAME} With \${VARIABLE}
    ...    [END] [name] Test Case \${NAME} With \${VARIABLE}

Test Case Name With ['My', 'List']
    Check Test Case    Test Case \${NAME} With \${MY LIST}
    Check Stdout Contains    SEPARATOR=\n
    ...    [Start] [name] Test Case \${NAME} With \${MY LIST}
    ...    [END] [name] Test Case \${NAME} With \${MY LIST}

Test Case Name With {'key': 'value'}
    Check Test Case    Test Case \${NAME} With \${MY DICT}
    Check Stdout Contains    SEPARATOR=\n
     ...    [Start] [name] Test Case \${NAME} With \${MY DICT}
    ...    [END] [name] Test Case \${NAME} With \${MY DICT}

Test Case Name With \${UNKONW VARIABLE}
    Check Test Case    Test Case \${NAME} With \${UNKONW VARIABLE}
    Check Stdout Contains    SEPARATOR=\n
    ...    [Start] [name] Test Case \${NAME} With \${UNKONW VARIABLE}
    ...    [END] [name] Test Case \${NAME} With \${UNKONW VARIABLE}
