*** Variables ***
${VARIABLE TABLE IN VARIABLES 2 (1)}         Initial value
${VARIABLE TABLE IN VARIABLES 2 (2)}         Initial value
${VARIABLE TABLE IN VARIABLES 2 (3)}         Initial value

*** Test Cases ***
Test Variables Set In One Suite Are Not Available In Another
    [Documentation]    Also checks that variables created in the variable table of the other suite are not available here.
    Variable Should Not Exist    $new_var
    Variable Should Not Exist    $uk_var_1
    Variable Should Not Exist    $uk_var_2
    Variable Should Not Exist    @uk_var_3
    Variable Should Not Exist    @uk_var_3
    Variable Should Not Exist    \${scalar}
    Variable Should Not Exist    \@{list}

Suite Variables Set In One Suite Are Not Available In Another
    Variable Should Not Exist    \${suite_setup_suite_var}
    Variable Should Not Exist    \@{suite_setup_suite_var}
    Variable Should Not Exist    \${test_level_suite_var}
    Variable Should Not Exist    \@{test_level_suite_var}
    Variable Should Not Exist    \${uk_level_suite_var}
    Variable Should Not Exist    \@{uk_level_suite_var}
    Variable Should Not Exist    $sub_uk_level_suite_var
    Variable Should Not Exist    @sub_uk_level_suite_var
    Variable Should Not Exist    $suite_teardown_suite_var
    Variable Should Not Exist    @suite_teardown_suite_var

Global Variables Set In One Suite Are Available In Another
    Should Be Equal    ${suite_setup_global_var}    Global var set in suite setup
    Should Be Equal    ${test_level_global_var}    Global var set in test
    Should Be Equal    ${uk_level_global_var}    Global var set in user keyword
    Should Be Equal    ${sub_uk_level_global_var}    Global var set in sub user keyword
    Should Be Equal    ${suite_teardown_global_var}    Global var set in suite teardown
    Should Be Equal    ${global_var_needing_escaping}    Four backslashes \\\\\\\\ and \\\${notvar}

Global Variable Set In One Suite Overrides Variable In Variable Table
    Should Be Equal    ${VARIABLE TABLE IN VARIABLES 2 (1)}    Set by suite setup in "__init__.robot"
    Should Be Equal    ${VARIABLE TABLE IN VARIABLES 2 (2)}    Set by suite setup in "variables.robot"
    Should Be Equal    ${VARIABLE TABLE IN VARIABLES 2 (3)}    Set by test in "variables.robot"

Set Child Suite Variable 3
    Should Be Equal    ${PARENT SUITE SETUP CHILD SUITE VAR 1}    Set in __init__
    Should Be Equal    ${PARENT SUITE SETUP CHILD SUITE VAR 2}    Overridden by global
    Should Be True    ${PARENT SUITE SETUP CHILD SUITE VAR 3} == {'Set': 'in __init__'}

Scopes And Overriding 3
    Should Be Equal    ${cli_var_1}    CLI1
    Should Be Equal    ${cli_var_2}    CLI2
    Should Be Equal    ${cli_var_3}    New value 3
    Should Be Equal    ${parent_suite_setup_global_var_to_reset}    Set in test!
    Should Be Equal    ${parent_suite_var_to_reset}    Set using Set Global Variable
    Should Be Equal    ${NEW GLOBAL VAR}    ${42}
