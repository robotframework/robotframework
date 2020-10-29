*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/DynamicLibraryWithoutGetKwArgsAndDoc.py
Resource          libdoc_resource.robot

*** Test Cases ***
Name
    Name Should Be    DynamicLibraryWithoutGetKwArgsAndDoc

Documentation
    Doc Should Be    Library doc set in class.

Version
    Version Should Be    ${EMPTY}

Type
    Type Should Be    LIBRARY

Generated
    Generated Should Be Defined

Scope
    Scope Should Be    TEST

Init
    Init Doc Should Be          0    Static __init__ doc.
    Init Arguments Should Be    0    doc=None

Keyword
    Keyword Name Should Be         0    Keyword
    Keyword Arguments Should Be    0    *varargs
    Keyword Doc Should Be          0    ${EMPTY}

Documentation set in __init__
    Run Libdoc And Parse Output    ${TESTDATADIR}/DynamicLibraryWithoutGetKwArgsAndDoc.py::New
    Doc Should Be    New
