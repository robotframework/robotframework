*** Settings ***
Suite Setup       Set Unicode Repr Object As Variable
Library           NonAsciiLibrary
Library           TraceLogArgsLibrary.py

*** Variables ***
@{VALUES}         a    b    c    d
${NON ASCII}      Hyvää 'Päivää'\n
&{DICT}           a=1    c=3

*** Test Cases ***
Only Mandatory Arguments
    Only Mandatory UK    arg1    arg2
    Only Mandatory    arg1    arg2

Mandatory And Default Arguments
    Mandatory And Default UK    mandatory
    Mandatory And Default    mandatory

Multiple Default Values
    Multiple Default Values UK    10    a3=30
    Multiple Default Values    10    a3=30

Named Arguments
    Mandatory and Default UK    mandatory    default=bar
    Mandatory and Default    mandatory    default=bar

Named Arguments when Name Is Not Matching
    Mandatory and Default UK    mandatory    foo=bar
    Mandatory and Default    mandatory    foo=bar

Variable Number of Arguments
    Mandatory and Varargs UK    @{VALUES}
    Mandatory and Varargs    @{VALUES}
    Mandatory and Varargs UK    mandatory    @{VALUES}
    Mandatory and Varargs    mandatory    @{VALUES}
    Mandatory and Varargs UK    mandatory
    Mandatory and Varargs    mandatory

Named only
    Named only UK    no1=a    no2=b
    Named only       no1=a    no2=b

Kwargs
    Kwargs UK
    Kwargs
    Kwargs UK    a=override    b=${2}    &{DICT}
    Kwargs       a=override    b=${2}    &{DICT}

All args
    All args UK    1    2    3    named_only=4    free=5
    All args       1    2    3    named_only=4    free=5

Non String Object as Argument
    Mandatory and Default UK    ${TRUE}    default=${1.0}
    Mandatory and Default    ${TRUE}    default=${1.0}
    Mandatory and Varargs UK    ${-123}    ${1.0}
    Mandatory and Varargs    ${-123}    ${1.0}

None as Argument
    Mandatory and Default UK    ${NONE}    default=${NONE}
    Mandatory and Default    ${NONE}    default=${NONE}
    Mandatory and Varargs UK    ${NONE}    ${NONE}
    Mandatory and Varargs    ${NONE}    ${NONE}

Non Ascii String as Argument
    Mandatory and Default UK    ${NON ASCII}    default=${NON ASCII}
    Mandatory and Default    ${NON ASCII}    default=${NON ASCII}
    Mandatory and Varargs UK    ${NON ASCII}    ${NON ASCII}
    Mandatory and Varargs    ${NON ASCII}    ${NON ASCII}

Object With Unicode Repr as Argument
    Mandatory And Default UK    ${object}    default=${object}
    Mandatory And Default    ${object}    default=${object}
    Mandatory and Varargs UK    ${object}    ${object}
    Mandatory and Varargs    ${object}    ${object}

Arguments With Run Keyword
    ${keyword name}=    Set Variable    Catenate
    ${result} =    Run Keyword    ${keyword name}    @{VALUES}
    Should Be Equal    ${result}    a b c d

Embedded Arguments
    Embedded Arguments "foo" and "${42}" with UK
    Embedded Arguments "bar" and "${TEST NAME}"
    Both embedded and normal arguments    argument
    Both embedded and normal arguments    normal=argument

*** Keywords ***
Set Unicode Repr Object As Variable
    ${object} =    Print and Return NonASCII Object
    Set Global Variable    ${OBJECT}

Only Mandatory UK
    [Arguments]    ${mand1}    ${mand2}
    No Operation

Mandatory And Default UK
    [Arguments]    ${mand}    ${default}=default value
    No Operation

Multiple Default Values UK
    [Arguments]    ${a1}=1    ${a2}=2    ${a3}=3    ${a4}=${4}
    No Operation

Mandatory and Varargs UK
    [Arguments]    ${mand}    @{vargs}
    No Operation

Named only UK
    [Arguments]    @{}    ${no1}=value    ${no2}
    No Operation

Kwargs UK
    [Arguments]    &{kwargs}
    No Operation

All args UK
    [Arguments]    ${positional}    @{varargs}    ${named_only}    &{kwargs}
    No Operation

Embedded Arguments "${first}" and "${second}" with ${what:[KU]+}
    Should Be Equal    ${first}    foo
    Should be Equal    ${second}    ${42}
    Should be Equal    ${what}    UK

Both ${embedded} and normal arguments
    [Arguments]     ${normal}
    Should Be Equal    ${embedded}    embedded
    Should Be Equal    ${normal}    argument
