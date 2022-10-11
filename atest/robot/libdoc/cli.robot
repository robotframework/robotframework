*** Settings ***
Resource         libdoc_resource.robot
Test Template    Run Libdoc And Verify Created Output File

*** Test Cases ***
Default format is got from output file extension
    String ${OUTHTML}            HTML         String
    String ${OUTXML}             XML          String    path=${OUTXML}

'*.libspec' extension creates XML file with HTML docs
    String ${OUTBASE}.libspec    LIBSPEC     String    path=${OUTBASE}.libspec

Using --format overrides output file extension
    -f XmL ${TESTDATADIR}/resource.robot ${OUTHTML}       XML         resource
    --format hTmL BuiltIn ${OUTBASE}.xxx                  HTML        BuiltIn     path=${OUTBASE}.xxx
    --format XML String ${OUTBASE}.libspec                XML         String      path=${OUTBASE}.libspec

Using --specdocformat to specify doc format in output
    --format XML --specdocformat RAW String ${OUTXML}              XML        String      path=${OUTXML}
    --format XML --specdocformat HTML String ${OUTXML}             LIBSPEC    String      path=${OUTXML}
    --format XML --specdocformat RAW String ${OUTBASE}.libspec     XML        String      path=${OUTBASE}.libspec
    --format XML --specdocformat HTML String ${OUTBASE}.libspec    LIBSPEC    String      path=${OUTBASE}.libspec

Library arguments
    ${TESTDATADIR}/LibraryArguments.py::required::true ${OUTHTML}    HTML    LibraryArguments

Library name matching spec extension
    --pythonpath ${DATADIR}/libdoc LIBPKG.JSON ${OUTXML}        XML    LIBPKG.JSON    path=${OUTXML}
    [Teardown]    Keyword Name Should Be    0    Keyword In Json

Library name matching resource extension
    --pythonpath ${DATADIR}/libdoc LIBPKG.resource ${OUTXML}    XML    LIBPKG.resource    path=${OUTXML}
    [Teardown]    Keyword Name Should Be    0    Keyword In Resource

Library argument matching resource extension
    ${TESTDATADIR}/LibraryArguments.py::required::true::foo.resource ${OUTHTML}    HTML    LibraryArguments

Library argument matching resource extension when import fails
    [Template]    Run libdoc and verify output
    NonExisting::foo.resource ${OUTHTML}
    ...    Importing library 'NonExisting' failed: ModuleNotFoundError: No module named 'NonExisting'
    ...    Traceback (most recent call last):
    ...    ${SPACE*2}None
    ...    PYTHONPATH:
    ...    *
    ...    ${USAGE TIP[1:]}

Override name and version
    --name MyName --version 42 String ${OUTHTML}    HTML    MyName    42
    -n MyName -v 42 -f xml BuiltIn ${OUTHTML}       XML     MyName    42

Missing destination subdirectory is created
    String ${NEWDIR_HTML}        HTML    String    path=${NEWDIR_HTML}
    String ${NEWDIR_XML}         XML     String    path=${NEWDIR_XML}

Quiet
    --quiet String ${OUTHTML}    HTML    String    quiet=True

Theme
    --theme DARK String ${OUTHTML}     HTML    String    theme=dark
    --theme light String ${OUTHTML}    HTML    String    theme=light
    --theme NoNe String ${OUTHTML}     HTML    String    theme=

Relative path with Python libraries
    [Template]    NONE
    ${dir in libdoc exec dir}=    Normalize Path     ${ROBOTPATH}/../TempDirInExecDir
    # Wait until possible other run executing this same test finishes.
    Wait Until Removed    ${dir in libdoc exec dir}    30s
    Create Directory    ${dir in libdoc exec dir}
    Create File    ${dir in libdoc exec dir}/MyLibrary.py    def my_keyword(): pass
    Run Libdoc And Parse Output    ${dir in libdoc exec dir}/MyLibrary.py
    Name Should Be    MyLibrary
    Keyword Name Should Be    0    My Keyword
    [Teardown]    Remove Directory    ${dir in libdoc exec dir}    recursively

Resource file in PYTHONPATH
    [Template]    NONE
    Run Libdoc And Parse Output    --pythonpath ${DATADIR}/libdoc resource.resource
    Name Should Be    resource
    Keyword Name Should Be    -1    Yay, I got new extension!

Non-existing resource
    [Template]    NONE
    ${stdout} =    Run Libdoc    nonexisting.resource whatever.xml
    Should Be Equal    ${stdout}     Resource file 'nonexisting.resource' does not exist.${USAGE TIP}\n

*** Keywords ***
Run Libdoc And Verify Created Output File
    [Arguments]    ${args}   ${format}    ${name}    ${version}=    ${path}=${OUTHTML}    ${theme}=    ${quiet}=False
    ${stdout} =    Run Libdoc    ${args}
    Run Keyword    ${format} Doc Should Have Been Created    ${path}    ${name}    ${version}
    File Should Have Correct Line Separators    ${path}
    IF    "${theme}"
        File Should Contain    ${path}    "theme": "${theme}"
    ELSE
        File Should Not Contain    ${path}    "theme":
    END
    IF    not ${quiet}
        Path to output should be in stdout    ${path}    ${stdout.rstrip()}
    ELSE
        Should be empty    ${stdout}
    END
    [Teardown]    Remove Output Files

HTML Doc Should Have Been Created
    [Arguments]    ${path}    ${name}    ${version}
    ${libdoc}=    Get File    ${path}
    Should Start With    ${libdoc}    <!DOCTYPE
    Should Contain    ${libdoc}    ${name}
    Should Contain    ${libdoc}    ${version}

XML Doc Should Have Been Created
    [Arguments]    ${path}    ${name}    ${version}    ${docformat}=ROBOT
    ${libdoc}=           Parse Xml    ${path}
    Set Test Variable    ${LIBDOC}
    Name Should Be       ${name}
    Format Should Be     ${docformat}
    Run Keyword If       "${version}"    Version Should Match    ${version}

LIBSPEC Doc Should Have Been Created
    [Arguments]    ${path}    ${name}    ${version}    ${docformat}=HTML
    ${libdoc}=           Parse Xml    ${path}
    Set Test Variable    ${LIBDOC}
    Name Should Be       ${name}
    Format Should Be     ${docformat}
    Run Keyword If       "${version}"    Version Should Match    ${version}

Path to output should be in stdout
    [Arguments]    ${path}    ${stdout}
    File Should Exist    ${stdout}
    Remove File    ${path}
    File Should Not Exist    ${stdout}
