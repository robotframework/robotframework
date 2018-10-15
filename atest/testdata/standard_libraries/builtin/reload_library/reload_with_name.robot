*** Settings ***
Library           Reloadable.py    WITH NAME    foo
Library           Reloadable.py    WITH NAME    bar

*** Test Cases ***
Reload with name
    [Documentation]    FAIL No keyword with name 'bar.added here' found.
    foo.Add keyword    added here
    Reload library    foo
    foo.added here
    bar.added here

Reload with instance
    [Documentation]    FAIL No keyword with name 'bar.added another' found.
    foo.Add keyword    added another
    foo.Reload self
    foo.added another
    bar.added another

Original name is not usable when import with WITH NAME
    [Documentation]    FAIL No library 'Reloadable' found.
    Reload library     Reloadable
