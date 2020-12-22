*** Test Cases ***
Import Library 1
    [Documentation]    Verify that keyword to be imported is not yet available
    ...                FAIL No keyword with name 'Directory Should Exist' found.
    Directory Should Exist    ${CURDIR}

Import Library 2
    Import Library    OperatingSystem
    Directory Should Exist    ${CURDIR}

Import Library 3
    [Documentation]    Verify that keyword from lib imported by earlier kw is still available
    Directory Should Exist    ${CURDIR}

Import Library With Arguments
    Import Library    ParameterLibrary    value    nön-äscii
    Parameters Should Be    value    nön-äscii

Import Library With Variables And WITH NAME
    ${name} =    Set Variable    ParameterLibrary
    Import Library    ${name}    ${42}    ${name}    WITH NAME    Variables-${42}
    Variables-42.Parameters Should Be    ${42}    ParameterLibrary

Import Library With WITH NAME containing non-ASCII spaces
    ${name} =    Set Variable    ParameterLibrary
    Import Library    ${name}    Ogham space mark    : :    WITH NAME    Ogham space mark
    Ogham space mark.Parameters Should Be    Ogham space mark    : :

Import Library Using Physical Path
    Import Library    ${CURDIR}${/}RegisteredClass.py
    RegisteredClass. Run Keyword If Method    False    Fail    This is not executed
    Import Library    ${CURDIR}/../../test_libraries/spaces in path/SpacePathLib.py
    ${ret} =    Spaces in Library Path
    Should Be Equal    ${ret}    here was a bug

Import Library Using Physical Path, Arguments And WITH NAME
    Import Library    ${CURDIR}/../../../testresources/testlibs/ParameterLibrary.py    first param    ${2}    WITH NAME    Params With Path
    Params With Path.Parameters Should Be    first param    ${2}

Import Library Arguments Are Resolved Only Once
    ${var} =    Set Variable    \${not var}
    Import Library    ParameterLibrary    c:\\temp    ${var}    WITH NAME    Escaping
    Escaping.Parameters Should Be    c:\\temp    \${not var}

Import Library With Named Arguments
    Import Library    ParameterLibrary    port=${2}    host=first    WITH NAME    Named
    Named.Parameters Should Be    first    ${2}

Import Library Failure Is Catchable
    [Documentation]    FAIL GLOB: Importing library 'NonExistingLib' failed: *Error: *
    Import Library    NonExistingLib

Import Library From Path
    Run Keyword And Expect Error    *    Keyword should exist    Print
    Import Library    ExampleLibrary.py
    Print    hello

Extra Spaces In Name Are Not Supported
    [Documentation]    FAIL GLOB: Importing library 'Date Time' failed: *Error: *
    Import Library    Date Time
