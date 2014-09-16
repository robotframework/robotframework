*** Settings ***
Library    UnicodeLibrary
Library    TraceLogArgsLibrary
Suite Setup  Set Unicode Repr Object As Variable


*** Variables ***
@{VALUES}  a  b  c  d
${NON ASCII}  Hyvää Päivää


*** Test cases ***
Only Mandatory Arguments
    Only Mandatory UK  arg1  arg2
    Only Mandatory  arg1  arg2

Mandatory And Default Arguments
    Mandatory And Default UK  mandatory
    Mandatory And Default  mandatory

Multiple Default Values
    Multiple Default Values UK  10  a3=30
    Multiple Default Values  10  a3=30

Named Arguments
    Mandatory and Default UK  mandatory  default=bar
    Mandatory and Default  mandatory  default=bar

Named Arguments when Name Is Not Matching
    Mandatory and Default UK  mandatory  foo=bar
    Mandatory and Default  mandatory  foo=bar

Variable Number of Arguments with UK
    Mandatory and Varargs UK  @{VALUES}
    Mandatory and Varargs UK  mandatory  @{VALUES}
    Mandatory and Varargs UK  mandatory

Variable Number of Arguments with Library Keyword
    Mandatory and Varargs  @{VALUES}
    Mandatory and Varargs  mandatory  @{VALUES}
    Mandatory and Varargs  mandatory

Arguments With Run Keyword
    ${keyword name}=  Set Variable  Log Many
    Run Keyword  ${keyword name}  @{VALUES}

Non String Object as Argument
    Mandatory and Default UK  ${TRUE}  default=${1.0}
    Mandatory and Default  ${TRUE}  default=${1.0}
    Mandatory and Varargs UK  ${-123}  ${1.0}
    Mandatory and Varargs  ${-123}  ${1.0}

None as Argument
    Mandatory and Default UK  ${NONE}  default=${NONE}
    Mandatory and Default  ${NONE}  default=${NONE}
    Mandatory and Varargs UK  ${NONE}  ${NONE}
    Mandatory and Varargs  ${NONE}  ${NONE}

Non Ascii String as Argument
    Mandatory and Default UK  ${NON ASCII}  default=${NON ASCII}
    Mandatory and Default  ${NON ASCII}  default=${NON ASCII}
    Mandatory and Varargs UK  ${NON ASCII}  ${NON ASCII}
    Mandatory and Varargs  ${NON ASCII}  ${NON ASCII}

Object With Unicode Repr as Argument
    Mandatory And Default UK  ${object}  default=${object}
    Mandatory And Default  ${object}  default=${object}
    Mandatory and Varargs UK  ${object}  ${object}
    Mandatory and Varargs  ${object}  ${object}


*** Keywords ***
Set Unicode Repr Object As Variable
    ${object} =  Print and Return Unicode Object
    Set Global Variable  ${OBJECT}

Only Mandatory UK
    [Arguments]  ${mand1}  ${mand2}
    No Operation

Mandatory And Default UK
    [Arguments]  ${mand}  ${default}=default value
    No Operation

Multiple Default Values UK
    [Arguments]  ${a1}=1  ${a2}=2  ${a3}=3  ${a4}=${4}
    No Operation

Mandatory and Varargs UK
    [Arguments]  ${mand}  @{vargs}
    No Operation
