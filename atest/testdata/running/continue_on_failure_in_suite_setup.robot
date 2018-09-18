*** Settings ***
Library  Exceptions
Suite Setup  Continuable Failure In User Keyword In Suite Setup

*** Test Cases ***
Not Executed
    [Documentation]  FAIL Can be continued
    No Operation

*** Keywords ***
Continuable Failure In User Keyword In ${where}
    Raise Continuable Failure
    Log  This should be executed in ${where} (with ∏ön ÄßÇïï €§)
