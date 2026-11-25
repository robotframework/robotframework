*** Settings ***
Test Metadata     Suite File    Set in the suite file

*** Test Cases ***
Inherited from init files and suite file
    No Operation

Own metadata wins
    [Metadata]    Priority    Critical
    No Operation

Remove inherited from parent init file
    [Metadata]    -Owner
    No Operation
