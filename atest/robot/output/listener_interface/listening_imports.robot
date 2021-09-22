*** Settings ***
Suite Setup       Run Tests    --listener "ListenImports;${IMPORTS FILE}"    ${LISTENER DIR}/imports/imports.robot
Suite Teardown    Remove Listener Files
Resource          listener_resource.robot

*** Variables ***
${IMPORTS FILE}    %{TEMPDIR}/listener_imports.txt

*** Test Cases ***
All imports are usable
    Check Test Case    ${TEST NAME}

Listen Imports
    Init Expect
    Expect
    ...    Library
    ...    BuiltIn
    ...    args: []
    ...    importer: None
    ...    originalname: BuiltIn
    ...    source: //BuiltIn.py
    Expect
    ...    Resource
    ...    another_resource
    ...    importer: //resource_with_imports.robot
    ...    source: //another_resource.robot
    Expect
    ...    Library
    ...    Process
    ...    args: []
    ...    importer: //resource_with_imports.robot
    ...    originalname: Process
    ...    source: //Process.py
    Expect
    ...    Resource
    ...    resource_with_imports
    ...    importer: //imports.robot
    ...    source: //resource_with_imports.robot
    Expect
    ...    Library
    ...    String
    ...    args: []
    ...    importer: //imports.robot
    ...    originalname: String
    ...    source: //String.py
    Expect
    ...    Library
    ...    Aliased
    ...    args: [\${2}]
    ...    importer: //imports.robot
    ...    originalname: local_lib
    ...    source: //local_lib.py
    Expect
    ...    Library
    ...    pythonmodule
    ...    args: []
    ...    importer: //imports.robot
    ...    originalname: pythonmodule
    ...    source: //pythonmodule/__init__.py
    Expect
    ...    Variables
    ...    vars.py
    ...    args: [name, value]
    ...    importer: //imports.robot
    ...    source: //vars.py
    Expect
    ...    Variables
    ...    vars.py
    ...    args: []
    ...    importer: //imports.robot
    ...    source: //vars.py
    Expect
    ...    Library
    ...    OperatingSystem
    ...    args: []
    ...    importer: None
    ...    originalname: OperatingSystem
    ...    source: //OperatingSystem.py
    Expect
    ...    Resource
    ...    dynamically_imported_resource
    ...    importer: None
    ...    source: //dynamically_imported_resource.robot
    Expect
    ...    Variables
    ...    vars.py
    ...    args: [new, args]
    ...    importer: None
    ...    source: //vars.py
    Verify Expected

Failed Impors Are Listed In Errors
    ${path} =    Normalize Path    ${LISTENER DIR}/imports/imports.robot
    Error in file    0    ${path}    9
    ...    Resource file 'resource that does not exist and fails' does not exist.
    Error in file    1    ${path}    10
    ...    Importing library 'LibraryThatDoesNotExist' failed: *
    ...    traceback=None
    Error in file    2    ${path}    11
    ...    Variable file 'variables which dont exist' does not exist.

*** Keywords ***
Init expect
    Set test variable    @{EXPECTED}    @{EMPTY}

Expect
    [Arguments]    ${type}    ${name}    @{attrs}
    ${entry} =    Catenate    SEPARATOR=\n\t
    ...    Imported ${type}
    ...    name: ${name}
    ...    @{attrs}
    Set test variable    @{EXPECTED}    @{EXPECTED}    ${entry}

Verify Expected
    Check Listener File    listener_imports.txt    @{EXPECTED}
