*** Settings ***
Library  Collections
Resource  resource_for_get_variables.robot
Variables  vars_for_get_variables.py
Suite Setup  Set Some Variables

*** Variables ***
${SCALAR}  dhrfad
@{LIST}    first    second
&{DICT}    a=1    b=2

*** Test Cases ***
Automatic and Command Line Variables
  Variables Should Contain  \${/}  \${cmd line}

Variable Table Scalar
  Variables Should Contain  \${SCALAR}

Variable Table List
  Variables Should Contain  \@{LIST}

Variable Table Dict
  Variables Should Contain  \&{DICT}

Global Variables
  Set Global In Resource
  Variables Should Contain  \${Global from suite setup}  \${GLOBAL FROM RESOURCE}

Suite Variables
  Set Suite Variable  ${Suite Var From Test}  Other value
  Variables Should Contain  \${Suite Var from suite setup}  \${Suite Var From Test}

Suite Variables 2
  Variables Should Contain  \${Suite Var from suite setup}  \${Suite Var From Test}

Resource File
  Variables Should Contain  \${RESOURCE VAR}

Variable File
  Variables Should Contain  \${var_in_variable_file}

Local Variables in Test Case Leak
  Variables Should Not Contain  \${local}
  ${local}=  Set Variable  lolcat
  Variables Should Contain  \${local}

Test Case Variable
  Set Test Variable  ${tc var}  tc
  Variables Should Contain  \${tc var}

Set Variable in User Keyword
  Set Var In UK

Variables Are Returned as NormalizedDict
  ${variables}=   Get Variables
  Should Be Equal  ${variables.__class__.__name__}  NormalizedDict
  Dictionary Should Contain Key  ${variables}  \${SCALAR}
  Dictionary Should Contain Key  ${variables}  \${__Scala__ R}
  ${copy}=  Copy Dictionary  ${variables}
  Dictionary Should Contain Key  ${copy}  \${SCALAR}
  Dictionary Should Contain Key  ${copy}  \${__Scala__ R}

Modifying Returned Variables Has No Effect On Real Variables
  ${variables}=   Get Variables
  Set To Dictionary    ${variables}    \${name}    value
  Variable Should Not Exist    ${name}

*** Keywords ***
Set Some Variables
  Set Suite Variable  ${Suite Var from suite setup}  Some value
  Set Global Variable  ${Global from Suite setup}  Some value

Set Var In UK
  ${uk var}=  Set Variable  foo
  Variables Should Contain  \${uk var}

Variables Should Contain
  [Arguments]  @{keys}
  ${variables}=  Get Variables
  :FOR  ${key}  IN  @{keys}
  \  Dictionary Should Contain Key  ${variables}  ${key}

Variables Should Not Contain
  [Arguments]  @{keys}
  ${variables}=  Get Variables
  :FOR  ${key}  IN  @{keys}
  \  Dictionary Should Not Contain Key  ${variables}  ${key}
