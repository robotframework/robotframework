*** Settings ***
Documentation  NO RIDE because it removes empty [Return]

*** Test Cases ***
    [Documentation]  FAIL  Test case name cannot be empty.
    Fail  Should not be executed

Empty Test Case
    [Documentation]  FAIL Test case contains no keywords.

Empty Test Case With Setup And Teardown
    [Documentation]  FAIL Test case contains no keywords.
    [Setup]  Fail  Should not be executed
    [Teardown]  Fail  Should not be executed

Empty User Keyword
    [Documentation]  FAIL User keyword 'Empty UK' contains no keywords.
    Empty UK

User Keyword With Only Non-Empty [Return] Works
    UK With Return

User Keyword With Empty [Return] Does Not Work
    [Documentation]  FAIL User keyword 'UK With Empty Return' contains no keywords.
    UK With Empty Return

Empty User Keyword With Other Settings Than [Return]
    [Documentation]  FAIL User keyword 'Empty UK With Settings' contains no keywords.
    Empty UK With Settings  argument

Non-Empty And Empty User Keyword
    [Documentation]  FAIL User keyword 'Empty UK' contains no keywords.
    UK
    Empty Uk
    Fail  We should not be here

Non-Empty UK Using Empty UK
    [Documentation]  FAIL User keyword 'Empty UK' contains no keywords.
    Non Empty UK Using Empty UK

*** Keywords ***
    [Documentation]  This keyword has no name
    [Arguments]  ${arg}=urg
    Fail   Should not be executed

Empty UK

Empty UK With Settings
    [Arguments]  ${arg}
    [Documentation]  Settings other than [Return] are not enough to make keyword non-empty

Non Empty UK Using Empty UK
    UK
    Empty UK

UK
    Log  In UK

UK With Return
    [Return]  This is a return value

UK With Empty Return
    [Return]
