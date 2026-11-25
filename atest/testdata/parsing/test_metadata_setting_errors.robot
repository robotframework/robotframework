*** Settings ***
Test Metadata     -Owner    value not allowed
Test Metadata     Valid     value

*** Test Cases ***
Value with removal in test is an error
    [Metadata]    -Valid    value not allowed
    No Operation
