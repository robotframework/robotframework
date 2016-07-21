*** Settings ***
Document    This is deprecated since RF 3.0.
...    Use *Documentation* instead.
Suite Precondition    Log    Suite Pre is deprecated
Suite Post Cond IT Ion:    Log    Suite Post is deprecated
Test Precondition:    Log    Test Pre is deprecated
testpostcondition    Log    Test Post is deprecated

*** Test Cases ***
Test Case
    [document]    This too is deprecated.
    [Pre Condition]    Log    [Pre] is deprecated
    [postcondition]    Log    [Post] is deprecated
    Keyword

Defaults
    No Operation

*** Keywords ***
Keyword
    [DOC U MENT]    And so is this.
    No Operation
