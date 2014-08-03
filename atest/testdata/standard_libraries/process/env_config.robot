*** Settings ***
Suite Setup       Set Environment Variable    var1    system
Resource          resource.robot

*** Variables ***
@{COMMAND}        python    -c    import os; print os.getenv('var1', '-'), os.getenv('var2', '-'), os.getenv('var3', '-')

*** Test Cases ***
By default environ is got from system
    ${result} =    Run Process    @{COMMAND}
    Should Be Equal    ${result.stdout}    system - -

Giving whole environ
    ${environ} =    Create environ    var2    environ
    ${result} =    Run Process    @{COMMAND}    env=${environ}
    Should Be Equal    ${result.stdout}    - environ -

Giving individual values
    ${result} =    Run Process    @{COMMAND}    shell=True    env:var2=individual
    Should Be Equal    ${result.stdout}    system individual -

Giving multiple values separately
    ${result} =    Run Process    @{COMMAND}    env:var2=ind1    env:var3=ind2
    Should Be Equal    ${result.stdout}    system ind1 ind2

Invividually given overrides system variable
    ${result} =    Run Process    @{COMMAND}    env:var1=override
    Should Be Equal    ${result.stdout}    override - -

Invividually given overrides value in given environ
    ${env} =    Create environ    var1    environ1    var2    environ2
    ${result} =    Run Process    @{COMMAND}    env:var3=new    env=${env}    env:var1=override
    Should Be Equal    ${result.stdout}    override environ2 new

*** Keywords ***
Create environ
    [Arguments]    @{environ}
    ${comspec} =    Get Environment Variable    COMSPEC    default=.
    ${path} =    Get Environment Variable    PATH    default=.
    ${systemroot} =    Get Environment Variable    SYSTEMROOT    default=.
    ${environ} =    Create Dictionary    @{environ}    PATH=${path}    SYSTEMROOT=${SYSTEMROOT}
    [Return]    ${environ}
