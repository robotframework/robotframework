*** Settings ***
Test Template    Keyword should exist
Resource         keyword_should_exist_resource_1.robot
Resource         keyword_should_exist_resource_2.robot

*** Variables ***
${LOG}  Log

*** Test Cases ***

Library keyword exists with short name
    Log
    L O G    Message isn't used

Library keyword exists with full name
    BuiltIn.Log
    built in . l o g

Local user keyword exists
    My User Keyword
    MYUSERKEYWORD

User keyword in resource exists with short name
    Resource Keyword
    Re Source Key Word

User keyword in resource exists with full name
    keyword_should_exist_resource_1.Resource Keyword
    KEYWORD_SHOULD_EXIST_RESOURCE_1.RESOURCE KEYWORD

Variables in keyword name
    ${LOG}
    ${LOG} Many

BDD style keyword exists
    Given this keyword exists
    Then this keyword exists
    ${LOG} this keyword exists

Keyword does not exist
    [Documentation]  FAIL No keyword with name 'Non Existing' found.
    Non Existing

Keyword does not exist with custom message
    [Documentation]  FAIL Custom message
    Non Existing  Custom message

Recommendations not shown if keyword does not exist
    [Documentation]  FAIL No keyword with name 'should be eQQual' found.
    should be eQQual

Duplicate keywords
    [Documentation]  FAIL
    ...  Multiple keywords with name 'Duplicated keyword' found. \
    ...  Give the full name of the keyword you want to use:\n
    ...  ${SPACE*4}keyword_should_exist_resource_1.Duplicated Keyword
    ...  ${SPACE*4}keyword_should_exist_resource_2.Duplicated Keyword
    Duplicated keyword

Duplicate keywords in same resource
    [Documentation]  FAIL Keyword with same name defined multiple times.
    Duplicate keyword in same resource

Higher priority keyword overrides
    No Operation

Empty keyword name
    [Documentation]  FAIL Keyword name cannot be empty.
    ${EMPTY}

Non-string keyword name
    [Documentation]  FAIL Keyword name must be a string.
    ${42}


*** Keywords ***
My User Keyword
    Fail  This is never executed

Duplicate keyword in same resource
    No Operation

Duplicate keyword in same resource
    No Operation

No Operation
    [Documentation]  Override keyword from BuiltIn
    No Operation

${Prefix} this ${keyword:keyword} exists
    Fail  Not executed
