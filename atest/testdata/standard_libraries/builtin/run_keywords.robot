*** Settings ***
Suite Setup  Run keywords  Passing  ${NOOP}
Suite Teardown  Run keywords  Failing  Passing  Fail

*** Variables ***
${NOOP}      No Operation
${PASSING}   Passing
${FAILING}   Failing
@{KEYWORDS}  ${NOOP}  ${PASSING}  Log Variables
${ERRORS}    Several failures occurred:\n\n1) Expected error message\n\n2) AssertionError
${TD ERR}    Parent suite teardown failed:\n${ERRORS}
${ATD ERR}   \n\nAlso parent suite teardown failed:\n${ERRORS}

*** Test Cases ***

Passing keywords
    [Documentation]  FAIL  ${TD ERR}
    Run keywords  No Operation  Passing  Log Variables

Failing keyword
    [Documentation]  FAIL  Expected error message${ATD ERR}
    Run keywords  Passing  Failing  Not Executed

Continuable failures
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) Expected continuable failure\n\n
    ...  2) Continuable 1/4\n\n
    ...  3) Continuable 2/4\n\n
    ...  4) Continuable 3/4\n\n
    ...  5) Continuable 4/4\n\n
    ...  6) Expected error message${ATD ERR}
    Run keywords  Continuable failure  Multiple continuables  Failing  Not Exec

Keywords as variables
    [Documentation]  FAIL  Expected error message${ATD ERR}
    Run keywords  ${NOOP}  ${PASSING}  @{KEYWORDS}  ${FAILING}

Non-existing variable as keyword name
    [Documentation]  FAIL  Variable '${NONEXISTING}' not found.${ATD ERR}
    Run keywords  Not Executed  ${NONEXISTING}  Not Executed

Non-existing keyword
    [Documentation]  FAIL  No keyword with name 'Non-Existing' found.${ATD ERR}
    Run keywords  Passing  Non-Existing  Non-Existing But Not Executed

Wrong number of arguments to keyword
    [Documentation]  FAIL  Keyword 'BuiltIn.Log' expected 1 to 5 arguments, got 0.${ATD ERR}
    Run keywords  Passing  Log  This isn't argument to Log keyword

In test setup
    [Documentation]  FAIL  Setup failed:\nExpected error message${ATD ERR}
    [Setup]  Run keywords  ${NOOP}  Passing  ${FAILING}  Not executed
    No Operation

In test teardown
    [Documentation]  FAIL  Teardown failed:\n
    ...  Several failures occurred:\n\n
    ...  1) Expected error message\n\n
    ...  2) AssertionError\n\n
    ...  3) No keyword with name 'Executed but doesn't exist' found.\n\n
    ...  4) No keyword with name 'Executed after syntax error in teardown' found.${ATD ERR}
    No Operation
    [Teardown]  Run keywords  Passing  ${NOOP}  Failing  ${NOOP}  Fail
    ...  Executed but doesn't exist
    ...  Executed after syntax error in teardown

In test teardown with ExecutionPassed exception
    [Documentation]  FAIL Stop here${ATD ERR}
    No Operation
    [Teardown]  Run Keywords
    ...    Returning keyword    AND
    ...    Pass Execution    Stop here    AND
    ...    Fail    Do not run me please
    Fail    Do not run me either

In test teardown with ExecutionPassed exception after continuable failure
    [Documentation]  FAIL Stop here${ATD ERR}
    No Operation
    [Teardown]  Run Keywords
    ...    Continuable failure    AND
    ...    Pass Execution    Stop here    AND
    ...    Fail    Do not run me please
    Fail    Do not run me either

*** Keywords ***

Passing
    Log  Hello, world!

Failing
    Fail  Expected error message

Continuable failure
    [Arguments]  ${msg}=Expected continuable failure
    Run keyword and continue on failure  Fail  ${msg}

Multiple continuables
    Continuable failure  Continuable 1/4
    Continuable failure  Continuable 2/4
    Continuable failure  Continuable 3/4
    Continuable failure  Continuable 4/4

Returning keyword
    Run Keywords    Return From Keyword
    Fail    Do not run me please
