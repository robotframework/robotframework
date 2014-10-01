*** Settings ***
Suite Teardown    Simple UK
Resource          resource.robot

*** Test Cases ***
Some other test
    [Documentation]  FAIL Keyword 'BuiltIn.Log' expected 1 to 5 arguments, got 0.
    Fail  Not actually executed so won't fail.
    Log
