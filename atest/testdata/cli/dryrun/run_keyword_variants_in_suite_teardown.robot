*** Settings ***
Suite Teardown  Run All Suite Teardown Related Run Keyword Variants

*** Test Cases ***
Suite Teardown Related Run Keyword Variants
    [Documentation]  FAIL
    ...    Parent suite teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Keyword 'BuiltIn.Log' expected 1 to 6 arguments, got 0.
    ...
    ...    2) No keyword with name 'Non Existing' found.
    ...
    ...    3) Keyword 'BuiltIn.Log' expected 1 to 6 arguments, got 9.
    No Operation

*** Keywords ***
Run All Suite Teardown Related Run Keyword Variants
    Run Keyword If All Tests Passed    Log
    Run Keyword If Any Tests Failed    Non Existing
    Run Keyword If All Tests Passed    Log    too    many    args   we    have    here    yes    we    do
