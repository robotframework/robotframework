*** Settings ***
Suite Teardown    Simple UK
Resource          resource.robot

*** Test Cases ***
Some other test
    [Documentation]    FAIL Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 4.
    Fail    Not actually executed so won't fail.
    Anarchy in the UK    Too    many    arguments    here
