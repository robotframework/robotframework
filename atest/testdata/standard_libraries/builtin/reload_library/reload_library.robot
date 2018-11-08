*** Settings ***
Library    Reloadable.py
Library    StaticLibrary.py
Library    module_library.py

*** Test Cases ***
Reload and add keyword
    Keyword should not exist    Added later
    Add keyword    Added later
    Reload library    Reloadable
    Keyword should exist    Added later

Reloading changes args
    [Documentation]    FAIL Keyword 'Reloadable.Original 1' expected 2 arguments, got 3.
    Original 1    takes one argument
    Add keyword    Original 1    arg1    arg2
    Reload library    Reloadable
    Original 1    now requires    two arguments
    Original 1    now    this    fails

Reloading can remove a keyword
    [Documentation]    FAIL STARTS:No keyword with name 'Original 2' found.
    Original 2    takes one argument
    Remove keyword    Original 2
    Reload library    Reloadable
    Original 2    takes one argument

Reloading with instance
    Add keyword    Original 3    arg1    arg2
    ${instance}=   Get library instance   Reloadable
    Reload library  ${instance}
    Original 3    arg1   arg2

Changes are reflected in next instance
    Added later
    Original 1    still takes    two arguments
    Keyword should not exist    Original 2
    Original 3    arg1   arg2

Reloading non-existing
    [Documentation]   FAIL No library 'NotThere' found.
    Reload library    NotThere

Reloading non-existing instance
    [Documentation]   FAIL No library '1' found.
    Reload library    ${1}

Reloading None fails
    [Documentation]   FAIL Library can not be None.
    Reload library    ${None}

Static library
    Keyword should not exist    Added Static
    Add static keyword    added_static
    Added Static    foo

Module library
    Keyword should not exist    Added module
    Add module keyword    added_module
    Reload library    module_library
    Added Module    foo

*** Keywords ***
Keyword should not exist
    [Arguments]    ${keyword}
    Run keyword and expect error    No keyword with name*    Keyword should exist    ${keyword}
