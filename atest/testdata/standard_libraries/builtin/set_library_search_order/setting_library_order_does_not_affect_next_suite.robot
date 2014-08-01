*** Settings ***
Library         TestLibrary.py  Library1  WITH NAME  Library1
Library         TestLibrary.py  Library2  WITH NAME  Library2

*** Test Cases ***
Default Library Order Should Be Suite Specific
    [Documentation]  FAIL Multiple keywords with name 'Get Name' found.\n Give the full name of the keyword you want to use.\n Found: 'Library1.Get Name' and 'Library2.Get Name'
    Get Name

