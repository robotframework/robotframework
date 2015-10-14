*** Settings ***
Suite Setup       Set Environment Variable    v1    system
Resource          process_resource.robot

*** Variables ***
@{COMMAND}        python    -c    import os; print(' '.join([os.getenv('v1', '-'), os.getenv('v2', '-'), os.getenv('v3', '-')]))

*** Test Cases ***
By default environ is got from system
    ${result} =    Run Process    @{COMMAND}
    Should Be Equal    ${result.stdout}    system - -

Giving whole environ
    ${environ} =    Create environ    v2    environ
    ${result} =    Run Process    @{COMMAND}    env=${environ}
    Should Be Equal    ${result.stdout}    - environ -

Giving individual values
    ${result} =    Run Process    @{COMMAND}    shell=True    env:v2=individual
    Should Be Equal    ${result.stdout}    system individual -

Giving multiple values separately
    ${result} =    Run Process    @{COMMAND}    env:v2=ind1    env:v3=ind2
    Should Be Equal    ${result.stdout}    system ind1 ind2

Invividually given overrides system variable
    ${result} =    Run Process    @{COMMAND}    env:v1=override
    Should Be Equal    ${result.stdout}    override - -

Invividually given overrides value in given environ
    ${env} =    Create environ    v1    environ1    v2    environ2
    ${result} =    Run Process    @{COMMAND}    env:v3=new    env=${env}    env:v1=override
    Should Be Equal    ${result.stdout}    override environ2 new

*** Keywords ***
Create environ
    [Arguments]    @{environ}
    ${comspec} =    Get Environment Variable    COMSPEC    default=.
    ${path} =    Get Environment Variable    PATH    default=.
    ${systemroot} =    Get Environment Variable    SYSTEMROOT    default=.
    ${environ} =    Create Dictionary    @{environ}    PATH=${path}    SYSTEMROOT=${SYSTEMROOT}
    [Return]    ${environ}
