*** Settings ***
Documentation        Old suite docs

*** Test Cases ***
Set test documentation
    Set test documentation      This has been set!\nTo several lines.
    Should be equal      ${TEST DOCUMENTATION}       This has been set!\nTo several lines.

Replace test documentation
   [Documentation]         This will be replaced
   Set test documentation      New doc
   Should be equal        ${TEST DOCUMENTATION}      New doc

Append to test documentation
   [Documentation]         Original doc
   Set test documentation      is continued    append please
   Should be equal        ${TEST DOCUMENTATION}      Original doc is continued
   Set test documentation      \n\ntwice!    append=yep
   Should be equal        ${TEST DOCUMENTATION}      Original doc is continued \n\ntwice!

Set suite documentation
   Set suite documentation     New suite doc
   Should be equal        ${SUITE DOCUMENTATION}      New suite doc

Set suite documentation 2
   Should be equal        ${SUITE DOCUMENTATION}      New suite doc

Append to suite documentation
   Set suite documentation      is continued    append please
   Should be equal        ${SUITE DOCUMENTATION}      New suite doc is continued

Append to suite documentation 2
   Should be equal        ${SUITE DOCUMENTATION}      New suite doc is continued
   Set suite documentation      \n\ntwice!    append=yep
   Should be equal        ${SUITE DOCUMENTATION}      New suite doc is continued \n\ntwice!

Set top level suite documentation
   Set suite documentation    Appended in test.    append=yes    top=please
   Should be equal        ${SUITE DOCUMENTATION}      New suite doc is continued \n\ntwice!
