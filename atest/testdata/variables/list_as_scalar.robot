*** Settings ***
Library         Collections
Variables       scalar_lists.py

*** Variables ***
@{LIST VAR}  spam  eggs  ${21}

*** Test Cases ***
Using List Variable As Scalar
    Log  ${LIST VAR}
    Should Be Equal  ${LIST VAR}  ${LIST}
    Should Be True  @{LIST VAR} == ${LIST VAR}
    Length Should Be  ${LIST VAR}  3

List Variable As Scalar With Extended Syntax
    Should Be Equal  ${LIST[0]} and ${LIST[1]}  spam and eggs
    Should Be Equal  ${list [2] * 2}  ${42}
    Should Be Equal  ${LIST.__len__()}  ${3}

Non-alphanumeric characters in name
    @{"spëciäl" ch@rs?!} =  Create List  @{LIST VAR}
    Should Be Equal  ${"spëciäl" ch@rs?!}  ${LIST VAR}

Access and Modify List Variable With Keywords From Collections Library
    Lists Should Be Equal  ${LIST VAR}  ${LIST}
    Append To List  ${LIST VAR}  new value
    List Should Contain Value  ${LIST VAR}  new value
    Remove Values From List  ${LIST VAR}  eggs
    Set List Value  ${LIST VAR}  0  ham
    Should Be True  ${LIST VAR} == ['ham', 21, 'new value']
    Reverse List  ${LIST VAR}
    Should Be Equal  ${LIST VAR}[0]  new value
    Should Be Equal  ${LIST VAR}[1]  ${21}
    Should Be Equal  ${LIST VAR}[-1]  ham

Modifications To List Variables Live Between Test Cases
    Should Be True  ${LIST VAR} == ['new value', 21, 'ham']
