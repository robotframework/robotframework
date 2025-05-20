*** Settings ***
Suite Setup       My Setup
Suite Teardown    My Teardown

*** Variables ***
${PARENT SUITE VAR TO RESET}    Initial value

*** Keywords ***
My Setup
    Set Test Variable     $parent_suite_setup_test_var    New in RF 7.2!
    Set Suite Variable    $parent_suite_setup_suite_var    Set in __init__
    Set Suite Variable    &parent_suite_setup_suite_var_2    children=true    children=false
    Set Suite Variable    $parent_suite_setup_child_suite_var_1    Set in __init__    children=true
    Set Suite Variable    @parent_suite_setup_child_suite_var_2    Set in    __init__    children=joojoo
    Set Suite Variable    &parent_suite_setup_child_suite_var_3    Set=in __init__    children=${42}
    Set Global Variable    $parent_suite_setup_global_var    Set in __init__
    Set Global Variable    $parent_suite_setup_global_var_to_reset    Orig
    Set Global Variable    ${VARIABLE TABLE IN VARIABLES 2 (1)}    Set by suite setup in "__init__.robot"
    Should Be Equal    ${PARENT SUITE VAR TO RESET}    Initial value
    Check Variables

My Teardown
    Should Be Equal    ${parent_suite_setup_test_var}    New in RF 7.2!
    Should Be Equal    ${parent_suite_setup_suite_var}    Set in __init__
    Should Be True     ${parent_suite_setup_suite_var_2} == {'children': 'true'}
    Should Be Equal    ${parent_suite_setup_child_suite_var_1}    Set in __init__
    Should Be Equal    ${parent_suite_setup_child_suite_var_2}    Overridden by global
    Should Be True     ${parent_suite_setup_child_suite_var_3} == {'Set': 'in __init__'}
    Should Be Equal    ${parent_suite_setup_global_var}    Set in __init__
    Should Be Equal    ${parent_suite_setup_global_var_to_reset}    Set in test!
    Should Be Equal    ${cli_var_1}    CLI1
    Should Be Equal    ${cli_var_2}    CLI2
    Should Be Equal    ${cli_var_3}    New value 3
    Should Be Equal    ${PARENT SUITE VAR TO RESET}    Set using Set Global Variable
    Should Be Equal    ${NEW GLOBAL VAR}    ${42}
    Set Test Variable  $parent_suite_setup_test_var    Overridden in teardown
    Check Variables    Overridden in teardown    Overridden by global    Set in test!

Check Variables
    [Arguments]    ${override1}=New in RF 7.2!    ${override2}=${{['Set in', '__init__']}}    ${override3}=Orig
    Should Be Equal    ${parent_suite_setup_test_var}               ${override1}
    Should Be Equal    ${parent_suite_setup_suite_var}              Set in __init__
    Should Be Equal    ${parent_suite_setup_suite_var_2}            ${{{'children': 'true'}}}
    Should Be Equal    ${parent_suite_setup_child_suite_var_1}      Set in __init__
    Should Be Equal    ${parent_suite_setup_child_suite_var_2}      ${override2}
    Should Be Equal    ${parent_suite_setup_child_suite_var_3}      ${{{'Set': 'in __init__'}}}
    Should Be Equal    ${parent_suite_setup_global_var}             Set in __init__
    Should Be Equal    ${parent_suite_setup_global_var_to_reset}    ${override3}
    Should Be Equal    ${VARIABLE TABLE IN VARIABLES 2 (1)}         Set by suite setup in "__init__.robot"
