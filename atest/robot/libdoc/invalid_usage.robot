*** Settings ***
Resource         libdoc_resource.robot
Test Setup       Remove File    ${OUT HTML}
Test Template    Run libdoc and verify error
Test Teardown    Should Not Exist    ${OUT HTML}

*** Variable ***
${USAGE TIP}    \nTry --help for usage information.\n

*** Test Cases ***

No arguments
    ${EMPTY}          Expected at least 2 arguments, got 0.

Too many arguments when creating output
    MyLib out.xml extra      Only two arguments allowed when writing output.

Too many arguments with version
    Dialogs version extra    Command 'version' does not take arguments.

Invalid option
    --invalid         option --invalid not recognized

Invalid format
    -f XXX BuiltIn ${OUT HTML}    Format must be 'HTML' or 'XML', got 'XXX'.
    BuiltIn out.ext            Format must be 'HTML' or 'XML', got 'EXT'.

Invalid doc format
    --docformat inv BuiltIn ${OUT HTML}    Doc format must be 'ROBOT', 'TEXT', 'HTML' or 'REST', got 'INV'.

Invalid doc format in library
    ${TESTDATADIR}/DocFormatInvalid.py ${OUT HTML}   Invalid documentation format 'INVALID'.

Non-existing library
    NonExistingLib ${OUT HTML}   Importing test library 'NonExistingLib' failed: *

Non-existing spec
    nonex.xml ${OUT HTML}    Spec file 'nonex.xml' does not exist.

Invalid spec
    [Setup]    Create File    ${OUT XML}    <wrong/>
    ${OUT XML} ${OUT HTML}    Invalid spec file '${OUT XML}'.
    [Teardown]    Remove File    ${OUT XML}

Non-XML spec
    [Setup]    Create File    ${OUT XML}    very wrong
    ${OUTXML} ${OUT HTML}    Building library '${OUT XML}' failed: *
    [Teardown]    Remove File    ${OUT XML}

Invalid resource
    ${CURDIR}/invalid_usage.robot ${OUT HTML}
    ...   [ ERROR ] *: Non-existing setting 'Test Setup'.
    ...   [ ERROR ] *: Non-existing setting 'Test Template'.
    ...   [ ERROR ] *: Non-existing setting 'Test Teardown'.
    ...   Resource file '*' contains a test case table which is not allowed.


*** Keywords ***
Run libdoc and verify error
    [Arguments]    ${args}    @{error}
    Run libdoc and verify output    ${args}    @{error}    ${USAGE TIP}
