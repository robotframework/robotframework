*** Settings ***
Library    libswithargs.Mandatory  first arg       another arg

Library    libswithargs.Defaults   m1                       WITH NAME  D1
Library    libswithargs.Defaults   m2  d1                   WITH NAME  D2
Library    libswithargs.Defaults   m3  ${1}  default2=${2}  WITH NAME  D3
Library    libswithargs.Defaults   mx  default2=xxx         WITH NAME  D4
Library    libswithargs.Defaults   mx  ${NOT NAMED}         WITH NAME  D5

Library    libswithargs.Varargs    m1              WITH NAME  V1
Library    libswithargs.Varargs    m2  v1          WITH NAME  V2
Library    libswithargs.Varargs    m3  ${1}  ${2}  WITH NAME  V3

Library    libswithargs.Mixed      m1              WITH NAME  M1
Library    libswithargs.Mixed      m2  d1          WITH NAME  M2
Library    libswithargs.Mixed      m3  d1          WITH NAME  M3
Library    libswithargs.Mixed      m4  d2  v       WITH NAME  M4
Library    libswithargs.Mixed      m5  d3  v1  v2  WITH NAME  M5

Variables  ../../testresources/res_and_var_files/different_variables.py
Library    libswithargs.Mixed      ${LIST1}  ${DICTIONARY1}  ${None}  ${42}
Library    libswithargs.Defaults   @{LIST WITH OBJECTS}

Library    libswithargs.Mandatory  too few
Library    libswithargs.Defaults
Library    libswithargs.Varargs

Library    libswithargs.Mandatory  too  many  args  here
Library    libswithargs.Defaults   too  many  args  here  too

Library    libswithargs.Mandatory  ${NONEXISTING}    ${NONEXISTING}

Library    Collections

Test Template    Verify Arguments


***Variables***
@{LIST WITH OBJECTS}  ${None}  ${1.0}  default2=not named
${NOT NAMED}    default2=xxx

*** Test Cases ***

Mandatory arguments
    libswithargs.Mandatory  first arg  another arg

Default values
    D1  m1  value  ${None}
    D2  m2  d1     ${None}
    D3  m3  ${1}   ${2}
    D4  mx  value  xxx
    D5  mx  default2=xxx  ${None}

Varargs
    V1  m1  ${EMPTY}
    V2  m2  v1
    V3  m3  1 2

Mixed
    M1  m1  ${42}  ${EMPTY}
    M2  m2  d1     ${EMPTY}
    M3  m3  d1     ${EMPTY}
    M4  m4  d2     v
    M5  m5  d3     v1 v2

Variables containing objects
    libswithargs.Mixed  ${LIST1}  ${DICTIONARY1}  None 42
    libswithargs.Defaults  ${None}  ${1.0}  default2=not named


***Keywords***

Verify arguments
    [Arguments]  ${lib}  @{expected args}
    ${actual args} =  Run Keyword  ${lib}.Get Args
    Lists should be equal  ${actual args}  ${expected args}
