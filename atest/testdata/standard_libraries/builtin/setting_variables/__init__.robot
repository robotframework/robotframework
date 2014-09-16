*** Settings ***
Suite Setup       My Setup
Suite Teardown    My Teardown

*** Keywords ***
My Setup
    Set Suite Variable    $parent_suite_setup_suite_var    Set in __init__
    Set Global Variable    $parent_suite_setup_global_var    Set in __init__
    Set Global Variable    $parent_suite_setup_global_var_to_reset    Orig

My Teardown
    Should Be Equal    ${parent_suite_setup_suite_var}    Set in __init__
    Should Be Equal    ${parent_suite_setup_global_var}    Set in __init__
    Should Be Equal    ${parent_suite_setup_global_var_to_reset}    Set in test!
    Should Be Equal    ${cli_var_1}    CLI1
    Should Be Equal    ${cli_var_2}    CLI2
    Should Be Equal    ${cli_var_3}    New value 3
