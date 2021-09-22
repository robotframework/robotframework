*** Settings ***
Resource          resource_with_imports.robot
Library           String
Library           local_lib.py    ${2}    WITH NAME    Aliased
Library           pythonmodule
Variables         vars.py    name    value
Variables         vars.py    name    value
Variables         vars.py
Resource          resource that does not exist and fails
Library           LibraryThatDoesNotExist
Variables         variables which dont exist

*** Test Cases ***
Dynamic imports
    Import library    OperatingSystem
    Import Resource    ${CURDIR}/dynamically_imported_resource.robot
    Import Variables    ${CURDIR}/vars.py    new    args

All imports are usable
    resource_with_imports.Foo
    another_resource.Ploo
    Process.Terminate All Processes
    String.Split to lines    foo
    Aliased.some kw
    pythonmodule.keyword
    OperatingSystem.Get file    ${CURDIR}/vars.py
    dynamically_imported_resource.Dyn
    Log   Check variables exist: ${name} ${new} ${my var}
