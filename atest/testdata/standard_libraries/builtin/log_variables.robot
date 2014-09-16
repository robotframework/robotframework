*** Setting ***
Suite Setup       My Suite Setup

*** Variable ***
@{LIST}           Hello    world
${SCALAR}         Hi tellus

*** Test Case ***
Previous Test
    No Operation

Log Variables
    [Setup]    Set Log Level    TRACE
    Log Variables
    ${var} =    Set Variable    Hello
    ${int_list} =    Evaluate    [ 0, 1, 2, 3 ]
    @{int_list} =    Evaluate    [ 0, 1, 2, 3 ]
    Log Variables    debug
    Log Variables In UK
    [Teardown]    Set Log Level    INFO

*** Keyword ***
My Suite Setup
    ${suite_setup_local_var} =    Set Variable    Variable available only locally    in suite setup
    Set Suite Variable    $suite_setup_suite_var    Suite var set in suite setup
    @{suite_setup_suite_var} =    Create List    Suite var set in    suite setup
    Set Suite Variable    @suite_setup_suite_var
    ${suite_setup_global_var} =    Set Variable    Global var set in suite setup
    Set Global Variable    $suite_setup_global_var
    Set Global Variable    @suite_setup_global_var    Global var set in    suite setup
    Log Variables

Log Variables In UK
    [Documentation]    Log Variables should log all the global variables, variables defined in test level and also the ones defined here in uk level
    ${ukvar} =    Set Variable    Value of an uk variable
    Log Variables
