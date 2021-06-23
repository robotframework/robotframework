*** Settings ***
Resource         libdoc_resource.robot
Test Setup       Remove File    ${OUT HTML}
Test Template    Run libdoc and verify error
Test Teardown    Should Not Exist    ${OUT HTML}

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
    -f XXX BuiltIn ${OUT HTML}               Format must be 'HTML', 'XML', 'JSON' or 'LIBSPEC', got 'XXX'.
    --format XML:XXX BuiltIn ${OUT HTML}     Format must be 'HTML', 'XML', 'JSON' or 'LIBSPEC', got 'XML:XXX'.
    --format XML:HTML BuiltIn ${OUT HTML}    Format must be 'HTML', 'XML', 'JSON' or 'LIBSPEC', got 'XML:HTML'.
    BuiltIn out.ext                          Format must be 'HTML', 'XML', 'JSON' or 'LIBSPEC', got 'EXT'.

Invalid specdocformat
    -s XXX BuiltIn ${OUT HTML}                Spec doc format must be 'RAW' or 'HTML', got 'XXX'.
    --specdocformat MD BuiltIn ${OUT HTML}    Spec doc format must be 'RAW' or 'HTML', got 'MD'.

Invalid specdocformat for HTML output format
    --specdocformat HTML BuiltIn ${OUT HTML}    The --specdocformat option is not applicable with HTML outputs.

Invalid doc format
    --docformat inv BuiltIn ${OUT HTML}    Doc format must be 'ROBOT', 'TEXT', 'HTML' or 'REST', got 'INV'.

Invalid doc format in library
    ${TESTDATADIR}/DocFormatInvalid.py ${OUT HTML}   Invalid documentation format 'INVALID'.

Non-existing library
    NonExistingLib ${OUT HTML}   Importing library 'NonExistingLib' failed: *

Non-existing spec
    nonex.xml ${OUT HTML}    Importing library 'nonex.xml' failed: *

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
    ...   ? ERROR ? Error in file '*' on line 3: Setting 'Test Setup' is not allowed in resource file.
    ...   ? ERROR ? Error in file '*' on line 4: Setting 'Test Template' is not allowed in resource file.
    ...   ? ERROR ? Error in file '*' on line 5: Setting 'Test Teardown' is not allowed in resource file.
    ...   Error in file '*[/\\]invalid_usage.robot' on line 7: Resource file with 'Test Cases' section is invalid.

Invalid output file
    [Setup]    Run Keywords
    ...    Remove File         ${OUT HTML}    AND
    ...    Create Directory    ${OUT HTML}    AND
    ...    Create Directory    ${OUT XML}
    String ${OUT HTML}    Opening Libdoc output file '${OUT HTML}' failed: *
    String ${OUT XML}     Opening Libdoc spec file '${OUT XML}' failed: *
    [Teardown]    Run Keywords
    ...    Remove Directory    ${OUT HTML}    AND
    ...    Remove Directory    ${OUT XML}

invalid Spec File version
    ${TESTDATADIR}/OldSpec.xml ${OUT XML}    Invalid spec file version 'None'. Robot Framework 4.0 and newer requires spec version 3.

*** Keywords ***
Run libdoc and verify error
    [Arguments]    ${args}    @{error}
    Run libdoc and verify output    ${args}    @{error}    ${USAGE TIP[1:]}
