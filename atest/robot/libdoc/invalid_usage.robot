*** Settings ***
Resource         libdoc_resource.robot
Test Setup       Remove File    ${OUT HTML}
Test Template    Run libdoc and verify error

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
    BuiltIn BuiltIn                          Format must be 'HTML', 'XML', 'JSON' or 'LIBSPEC', got ''.

Invalid specdocformat
    -s XXX BuiltIn ${OUT HTML}                Spec doc format must be 'RAW' or 'HTML', got 'XXX'.
    --specdocformat MD BuiltIn ${OUT HTML}    Spec doc format must be 'RAW' or 'HTML', got 'MD'.

Invalid specdocformat for HTML output format
    --specdocformat HTML BuiltIn ${OUT HTML}    The --specdocformat option is not applicable with HTML outputs.

Invalid doc format
    --docformat inv BuiltIn ${OUT HTML}    Doc format must be 'ROBOT', 'TEXT', 'HTML' or 'REST', got 'INV'.

Invalid doc format in library
    ${TESTDATADIR}/DocFormatInvalid.py ${OUT HTML}   Invalid documentation format 'INVALID'.

Invalid theme
    --theme bad String ${OUT XML}                    Theme must be 'DARK', 'LIGHT' or 'NONE', got 'BAD'.
    --theme light --format xml String ${OUT XML}     The --theme option is only applicable with HTML outputs.

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
    ${TESTDATADIR}/invalid_resource.resource ${OUT HTML}
    ...   ? ERROR ? Error in file '*[/\\]invalid_resource.resource' on line 2: Setting 'Metadata' is not allowed in resource file.
    ...   ? ERROR ? Error in file '*[/\\]invalid_resource.resource' on line 3: Setting 'Test Setup' is not allowed in resource file.
    ...   Error in file '*[/\\]invalid_resource.resource' on line 5: Resource file with 'Test Cases' section is invalid.

Invalid resource with '.robot' extension
    ${TESTDATADIR}/invalid_resource.robot ${OUT HTML}
    ...   ? ERROR ? Error in file '*[/\\]invalid_resource.robot' on line 2: Setting 'Metadata' is not allowed in resource file.
    ...   ? ERROR ? Error in file '*[/\\]invalid_resource.robot' on line 3: Setting 'Test Setup' is not allowed in resource file.
    ...   ${OUT HTML}
    ...   fatal=False

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

Invalid Spec File version
    ${TESTDATADIR}/OldSpec.xml ${OUT XML}    Invalid spec file version 'None'. Supported versions are 3, 4, 5, and 6.

*** Keywords ***
Run libdoc and verify error
    [Arguments]    ${args}    @{error}    ${fatal}=True
    IF    ${fatal}
        Run Libdoc And Verify Output    ${args}    @{error}    ${USAGE TIP[1:]}
        File Should Not Exist    ${OUT HTML}
    ELSE
        Run Libdoc And Verify Output    ${args}    @{error}
        File Should Exist    ${OUT HTML}
    END
