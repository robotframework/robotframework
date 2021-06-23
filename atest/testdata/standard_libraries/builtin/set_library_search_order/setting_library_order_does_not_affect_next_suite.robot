*** Settings ***
Library           TestLibrary.py    Library1    WITH NAME    Library1
Library           TestLibrary.py    Library2    WITH NAME    Library2

*** Test Cases ***
Default Library Order Should Be Suite Specific
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Get Name' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}Library1.Get Name
    ...    ${SPACE*4}Library2.Get Name
    Get Name
