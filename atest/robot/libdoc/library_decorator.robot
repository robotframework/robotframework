*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/LibraryDecorator.py
Resource          libdoc_resource.robot

*** Test Cases ***
Version
    Version should be    3.2b1

Scope
    Scope Should Be      global

Doc format
    Format Should Be     HTML

Keywords
    Keyword Name Should Be    0    Kw
    Keyword Count Should Be    1
