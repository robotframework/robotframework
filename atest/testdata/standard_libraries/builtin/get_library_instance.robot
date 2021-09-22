*** Settings ***
Library           OperatingSystem
Library           module_library
Library           ParameterLibrary    first    WITH NAME    1st
Library           ParameterLibrary    second    WITH NAME    2nd has spaces
Library           ParameterLibrary    same1    WITH NAME    Same when normalized
Library           ParameterLibrary    same2    WITH NAME    samewhen N O R M A L ized
Library           libraryscope.Test
Library           libraryscope.Suite
Library           libraryscope.Global
Library           Collections

*** Test Cases ***
Library imported normally
    ${lib} =    Get Library Instance    BuiltIn
    Should Be Equal    ${lib.convert_to_integer('42')}    ${42}
    ${lib} =    Get Library Instance    Operating System
    Should Not Be Empty    ${lib.list_directory('.')}

Module library
    ${lib} =    Get Library Instance    module_library
    Should Be Equal    ${lib.returning()}    Hello from module library

Library with alias
    [Documentation]    FAIL No library 'ParameterLibrary' found.
    ${lib} =    Get Library Instance    1st
    Should Be Equal    ${lib.parameters()[0]}    first
    ${lib} =    Get Library Instance    2nd has spaces
    Should Be Equal    ${lib.parameters()[0]}    second
    Get Library Instance    ParameterLibrary

Non-exact name
    ${lib} =    Get Library Instance    1 S T
    Should Be Equal    ${lib.parameters()[0]}    first
    ${lib} =    Get Library Instance    2NDHASSPACES
    Should Be Equal    ${lib.parameters()[0]}    second

Same name when normalized matching exactly
    ${lib} =    Get Library Instance    Same when normalized
    Should Be Equal    ${lib.parameters()[0]}    same1
    ${lib} =    Get Library Instance    samewhen N O R M A L ized
    Should Be Equal    ${lib.parameters()[0]}    same2

Same name when normalized matching multiple
    [Documentation]    FAIL Multiple libraries matching 'Same When Normalized' found.
    Get Library Instance    Same When Normalized

`Import Library` keyword
    Import Library    String
    ${lib} =    Get Library Instance    String
    Should Be Equal    ${lib.replace_string('Hello', 'e', 'i')}    Hillo

Non-existing library should cause catchable error
    Run Keyword And Expect Error    No library 'NonExisting' found.    Get Library Instance    NonExisting

Library scopes 1
    ${test} =    Get Library Instance    libraryscope.Test
    ${suite} =    Get Library Instance    libraryscope.Suite
    ${global} =    Get Library Instance    libraryscope.Global
    Log    ${test.register('Test 1')}
    Log    ${suite.register('Suite 1')}
    Log    ${global.register('Global 1')}
    Log    ${test.should_be_registered('Test 1')}
    Log    ${suite.should_be_registered('Suite 1')}
    Log    ${global.should_be_registered('Global 1')}

Library scopes 2
    ${test} =    Get Library Instance    libraryscope.Test
    ${suite} =    Get Library Instance    libraryscope.Suite    all=False
    ${global} =    Get Library Instance    libraryscope.Global    all=
    Log    ${test.register('Test 2')}
    Log    ${suite.register('Suite 2')}
    Log    ${global.register('Global 2')}
    Log    ${test.should_be_registered('Test 2')}
    Log    ${suite.should_be_registered('Suite 1', 'Suite 2')}
    Log    ${global.should_be_registered('Global 1', 'Global 2')}

Get all libraries
    &{libs} =    Get library instance    all=True
    Should contain keys    ${libs}
    ...    OperatingSystem
    ...    module_library
    ...    1st
    ...    2nd has spaces
    ...    libraryscope.Test
    ...    libraryscope.Suite
    ...    libraryscope.Global
    ...    Collections
    ...    BuiltIn
    ...    String
    Should Be Equal    ${libs.String.replace_string('Hello', 'e', 'i')}    Hillo

Get all libraries gets a copy
    &{libs} =    Get library instance    name is ignored when all is true    all=True
    Set to dictionary    ${libs}    foo=bar
    Dictionary should contain key    ${libs}    foo
    &{libs} =    Get library instance    all=yes
    Dictionary should not contain key    ${libs}    foo

*** Keywords ***
Should contain keys
    [Arguments]    ${dict}    @{keys}
    FOR    ${key}    IN    @{keys}
        Dictionary should contain key    ${dict}    ${key}
    END
