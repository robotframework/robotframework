*** Setting ***

*** Variable ***

*** Test Case ***
Check Test Vars Set In One Suite Are Not Available In Another
    [Documentation]    Also checks that variables created in the variable table of the other suite are not available here.
    Variable Should Not Exist    $new_var
    Variable Should Not Exist    $uk_var_1
    Variable Should Not Exist    $uk_var_2
    Variable Should Not Exist    @uk_var_3
    Variable Should Not Exist    @uk_var_3
    Variable Should Not Exist    \${scalar}
    Variable Should Not Exist    \@{list}

Check Suite Vars Set In One Suite Are Not Available In Another
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

Check Global Vars Set In One Suite Are Available In Another
    Should Be Equal    ${suite_setup_global_var}    Global var set in suite setup
    Should Be Equal    ${test_level_global_var}    Global var set in test
    Should Be Equal    ${uk_level_global_var}    Global var set in user keyword
    Should Be Equal    ${sub_uk_level_global_var}    Global var set in sub user keyword
    Should Be Equal    ${suite_teardown_global_var}    Global var set in suite teardown
    Should Be Equal    ${global_var_needing_escaping}    Four backslashes \\\\\\\\ and \\\${notvar}

Scopes And Overriding 3
    [Documentation]    Parts 1 & 2 are in builtin_variables
    Should Be Equal    ${cli_var_1}    CLI1
    Should Be Equal    ${cli_var_2}    CLI2
    Should Be Equal    ${cli_var_3}    New value 3

*** Keyword ***
