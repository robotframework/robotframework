*** Settings ***
Resource          libdoc_resource.robot
Test Template     Library Should Have No Init

*** Test Cases ***
New Style Python Class With No Init
    NewStyleNoInit.py

Old Style Python Class With No Argument Init
    no_arg_init.py

*** Keywords ***
Library Should Have No Init
    [Arguments]    ${library}    @{posonly marker}
    Run Libdoc And Parse Output    ${TESTDATADIR}/${library}
    Should Have No Init
    Doc Should Be                  No inits here!
    Keyword Name Should Be         0    Keyword
    Keyword Arguments Should Be    0    arg1    arg2    @{posonly marker}
    Keyword Doc Should Be          0    The only lonely keyword.
