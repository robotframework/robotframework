*** Settings ***
Suite Setup       Fail    Not Executed
Library           TheseDotNotExist
Resource          but_they_are_not
Variables         imported    either

*** Variables ***
${VARIABLE}      ${NON-EXISTING}

*** Test Cases ***
Test 1
    [Documentation]    FAIL Parent suite setup failed:
    ...    Expected failure in higher level setup
    Fail    Not executed
