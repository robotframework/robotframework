*** Settings ***
Suite Setup       Run Tests With Listeners
Suite Teardown    Remove Listener Files
Force Tags        regression
Default Tags      pybot    jybot
Resource          listener_resource.robot

*** Variables ***
${IMPORTS FILE}    %{TEMPDIR}/listener_imports.txt

*** Test Cases ***
Listen Imports
    Check Test Case   Do dynamic imports and check all imports are usable
    Init Expect
    Expect    Library    BuiltIn    args: []    importer: None    original_name: BuiltIn    source: //BuiltIn.py
    Expect    Resource    another_resource    importer: //resource_with_imports.robot    source: //another_resource.robot
    Expect    Library    Process    args: []    importer: //resource_with_imports.robot    original_name: Process    source: //Process.py
    Expect    Resource    resource_with_imports    importer: //imports.robot    source: //resource_with_imports.robot
    Expect    Library    String    args: []    importer: //imports.robot    original_name: String    source: //String.py
    Expect    Library    Aliased    args: [\${2}]    importer: //imports.robot    original_name: local_lib    source: //local_lib.py
    Java Expect    Library    ExampleJavaLibrary    args: []    importer: //imports.robot    original_name: ExampleJavaLibrary    source: None
    Expect    Library    pythonmodule    args: []    importer: //imports.robot    original_name: pythonmodule    source: //pythonmodule/__init__.py
    Expect    Variables    vars.py    args: [name, value]    importer: //imports.robot    source: //vars.py
    Expect    Variables    vars.py    args: []    importer: //imports.robot    source: //vars.py
    Expect    Library    OperatingSystem    args: []    importer: None    original_name: OperatingSystem    source: //OperatingSystem.py
    Expect    Resource    dynamically_imported_resource    importer: None    source: //dynamically_imported_resource.robot
    Expect    Variables    vars.py    args: [new, args]    importer: None    source: //vars.py
    Check Listener File    listener_imports.txt    @{expected}
    Check Syslog Contains    Resource file 'resource that does not exist and fails' does not exist.
    Check Syslog Contains    Importing test library 'librarythatdoesnotexist' failed:
    Check Syslog Contains    Variable file 'variables which dont exist' does not exist.

*** Keywords ***
Run Tests With Listeners
    Run Tests    --listener ListenImports:${IMPORTS FILE}    output/listeners/imports/imports.robot

Init expect
    Set test variable    @{expected}    @{EMPTY}

Expect
    [Arguments]    ${type}    ${name}    @{attrs}
    ${entry} =    Catenate    SEPARATOR=\n\t    Imported ${type}    name: ${name}    @{attrs}
    Set test variable    @{expected}    @{expected}    ${entry}

Java Expect
    [Arguments]    ${type}    ${name}    @{attrs}
    Run keyword if    $JYTHON    Expect    ${type}    ${name}    @{attrs}
