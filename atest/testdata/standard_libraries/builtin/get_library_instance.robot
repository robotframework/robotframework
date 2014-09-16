*** Settings ***
Library  OperatingSystem
Library  module_library
Library  ExampleJavaLibrary
Library  ParameterLibrary  first   WITH NAME  1st
Library  ParameterLibrary  second  WITH NAME  2nd
Library  libraryscope.Test
Library  libraryscope.Suite
Library  libraryscope.Global


*** Test Cases ***

Library imported normally
    ${lib} =  Get Library Instance  BuiltIn
    Should Be Equal  ${lib.convert_to_integer('42')}  ${42}
    ${lib} =  Get Library Instance  Operating System
    Should Not Be Empty  ${lib.list_directory('.')}    

Module library
    ${lib} =  Get Library Instance  module_library
    Should Be Equal  ${lib.returning()}  Hello from module library

Java library
    ${lib} =  Get Library Instance  ExampleJavaLibrary
    Should Be Equal  ${lib.getCount()}  ${1}
    Should Be Equal  ${lib.getCount()}  ${2}
    Should Be Equal  ${lib.getCount()}  ${3}

Library with alias
    [Documentation]  FAIL  No library with name 'ParameterLibrary' found.
    ${lib} =  Get Library Instance  1st
    Should Be Equal  ${lib.parameters()[0]}  first
    ${lib} =  Get Library Instance  2nd
    Should Be Equal  ${lib.parameters()[0]}  second
    Get Library Instance  ParameterLibrary

`Import Library` keyword
    Import Library  String
    ${lib} =  Get Library Instance  String
    Should Be Equal  ${lib.replace_string('Hello', 'e', 'i')}  Hillo

Non-existing library should cause catchable error
    Run Keyword And Expect Error  No library with name 'NonExisting' found.
    ...  Get Library Instance  NonExisting

Library scopes 1
    ${test} =  Get Library Instance  libraryscope.Test
    ${suite} =  Get Library Instance  libraryscope.Suite
    ${global} =  Get Library Instance  libraryscope.Global
    Log  ${test.register('Test 1')}
    Log  ${suite.register('Suite 1')}
    Log  ${global.register('Global 1')}
    Log  ${test.should_be_registered('Test 1')}
    Log  ${suite.should_be_registered('Suite 1')}
    Log  ${global.should_be_registered('Global 1')}

Library scopes 2
    ${test} =  Get Library Instance  libraryscope.Test
    ${suite} =  Get Library Instance  libraryscope.Suite
    ${global} =  Get Library Instance  libraryscope.Global
    Log  ${test.register('Test 2')}
    Log  ${suite.register('Suite 2')}
    Log  ${global.register('Global 2')}
    Log  ${test.should_be_registered('Test 2')}
    Log  ${suite.should_be_registered('Suite 1', 'Suite 2')}
    Log  ${global.should_be_registered('Global 1', 'Global 2')}
