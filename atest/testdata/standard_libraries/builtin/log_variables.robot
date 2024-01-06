*** Settings ***
Suite Setup       My Suite Setup

*** Variables ***
@{LIST}           Hello    world
${SCALAR}         Hi tellus
&{DICT}           key=value    two=${2}
${ITERABLE}       ${{(item for item in 'Should not be consumed!'.split())}}
${ENDLESS}        ${{itertools.repeat('RF')}}

*** Test Cases ***
Previous Test
    No Operation

Log Variables
    [Setup]    Set Log Level    TRACE
    Log Variables
    ${var} =    Set Variable    Hello
    ${int_list_1} =    Evaluate    [0, 1, 2, 3]
    @{int_list_2} =    Evaluate    [0, 1, 2, 3]
    Log Variables    debug
    Log Variables In UK
    Should Be Equal    ${{' '.join($ITERABLE)}}    Should not be consumed!
    [Teardown]    Set Log Level    INFO

List and dict variables failing during iteration
    Import Variables    ${CURDIR}/broken_containers.py
    Log Variables
    Log Many    ${BROKEN ITERABLE}    ${BROKEN SEQUENCE}    ${BROKEN MAPPING}

*** Keywords ***
My Suite Setup
    ${suite_setup_local_var} =    Set Variable    Variable available only locally in suite setup
    Set Suite Variable    $suite_setup_suite_var    Suite var set in suite setup
    @{suite_setup_suite_var_list} =    Create List    Suite var set in    suite setup
    Set Suite Variable    @suite_setup_suite_var_list
    ${suite_setup_global_var} =    Set Variable    Global var set in suite setup
    Set Global Variable    $suite_setup_global_var
    Set Global Variable    @suite_setup_global_var_list    Global var set in    suite setup
    Log Variables

Log Variables In UK
    [Documentation]    Log Variables should log all the global variables, variables defined in test level and also the ones defined here in uk level
    ${ukvar} =    Set Variable    Value of an uk variable
    Log Variables
