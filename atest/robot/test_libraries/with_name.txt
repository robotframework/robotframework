*** Settings ***
Suite Setup     Run 'With Name' Tests
Force Tags      regression
Default Tags    pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***
Import Library Normally Before Importing With Name In Another Suite
    ${test} =  Check Test Case  Import Library Normally Before Importing With Name In Another Suite
    Should Be Equal  ${test.kws[0].name}  OperatingSystem.Should Exist
    Should Be Equal  ${test.kws[1].name}  \${p1}, \${p2} = ParameterLibrary.Parameters
    Check Syslog Contains  Imported library 'OperatingSystem' with arguments [ ] (version ${ROBOT VERSION}, class type, global scope,
    Check Syslog Contains  Imported library 'ParameterLibrary' with arguments [ before1 | before2 ] (version <unknown>, class type, testcase scope,

Import Library With Name Before Importing With Name In Another Suite
    ${test} =  Check Test Case  Import Library With Name Before Importing With Name In Another Suite
    Should Be Equal  ${test.kws[0].name}  \${p1}, \${p2} = Params.Parameters
    Check Syslog Contains  Imported library 'ParameterLibrary' with arguments [ after1 | after2 ] (version <unknown>, class type, testcase scope,

Import Library Normally After Importing With Name In Another Suite
    ${test} =  Check Test Case  Import Library Normally After Importing With Name In Another Suite
    Should Be Equal  ${test.kws[0].name}  OperatingSystem.Should Exist
    Should Be Equal  ${test.kws[1].name}  \${p1}, \${p2} = ParameterLibrary.Parameters

Import Library With Name After Importing With Name In Another Suite
    ${test} =  Check Test Case  Import Library With Name After Importing With Name In Another Suite
    Should Be Equal  ${test.kws[0].name}  \${a1}, \${a2} = Params.Parameters

Name Given Using "With Name" Can Be Reused In Different Suites
    ${test} =  Check Test Case  Import Library With Name Before Importing With Name In Another Suite
    Should Be Equal  ${test.kws[0].name}  \${p1}, \${p2} = Params.Parameters
    ${test} =  Check Test Case  Name Given Using "With Name" Can Be Reused in Different Suites
    Should Be Equal  ${test.kws[0].name}  Params.Keyword In My Lib File
    Check Log Message  ${test.kws[0].msgs[0]}  Here we go!!
    ${test} =  Check Test Case  Import Library With Name After Importing With Name In Another Suite
    Should Be Equal  ${test.kws[0].name}  \${a1}, \${a2} = Params.Parameters

No Arguments
    ${test} =  Check Test Case  No Arguments
    Should Be Equal  ${test.kws[0].name}  OS.Directory Should Exist
    Should Be Equal  ${test.kws[1].name}  OS.Should Exist
    Check Syslog Contains  Imported library 'OperatingSystem' with name 'OS'

Arguments Containing Variables And Import Same Library Twice
    ${test} =  Check Test Case  Arguments Containing Variables And Import Same Library Twice
    Should Be Equal  ${test.kws[0].name}  \${a1}, \${a2} = Param1.Parameters
    Should Be Equal  ${test.kws[3].name}  \${a1}, \${a2} = Param2.Parameters
    Check Syslog Contains  Imported library 'ParameterLibrary' with arguments [ 1 | 2 ] (version <unknown>, class type, testcase scope,
    Check Syslog Contains  Imported library 'ParameterLibrary' with name 'Param1'
    Check Syslog Contains  Imported library 'ParameterLibrary' with arguments [ VAR | 42 ] (version <unknown>, class type, testcase scope,
    Check Syslog Contains  Imported library 'ParameterLibrary' with name 'Param2'

Alias Containing Variable
    Check Test Case  Alias Containing Variable

With Name Has No Effect If Not Second Last
    ${test} =  Check Test Case  With Name Has No Effect If Not Second Last
    Should Be Equal  ${test.kws[0].name}  \${a1}, \${a2} = ParameterLibrary.Parameters
    Check Syslog Contains  Imported library 'ParameterLibrary' with arguments [ whatever | with name ] (version <unknown>, class type, testcase scope,

With Name After Normal Import
    ${test} =  Check Test Case  With Name After Normal Import
    Should Be Equal  ${test.kws[0].name}  B2.Fail
    Check Syslog Contains  Imported library 'BuiltIn' with name 'B2'

Module Library
    ${test} =  Check Test Case  Module Library
    Should Be Equal  ${test.kws[0].name}  MOD1.Argument
    Should Be Equal  ${test.kws[1].name}  \${s} = mod 2.Keyword From Submodule
    Should Be Equal  ${test.kws[3].name}  MOD1.Failing
    Check Syslog Contains  Imported library 'module_library' with name 'MOD1'
    Check Syslog Contains  Imported library 'pythonmodule.library' with name 'mod 2'

Java Library
    [Tags]  jybot
    ${test} =  Check Test Case  Java Library
    Should Be Equal  ${test.kws[0].name}  \${s} = Java Lib.Return String From Library
    Should Be Equal  ${test.kws[2].name}  \${obj} = Java Lib.Get Java Object
    Check Syslog Contains  Imported library 'ExampleJavaLibrary' with name 'Java Lib'

Java Library In Package
    [Tags]  jybot
    ${test} =  Check Test Case  Java Library In Package
    Should Be Equal  ${test.kws[0].name}  \${s1} = Java Pkg.Return Value
    Should Be Equal  ${test.kws[1].name}  \${s2} = Java Pkg.Return Value
    Check Syslog Contains  Imported library 'javapkg.JavaPackageExample' with name 'Java Pkg'

Import Library Keyword
    ${test} =  Check Test Case  Import Library Keyword
    Should Be Equal  ${test.kws[1].name}  MyOS.Directory Should Exist
    Should Be Equal  ${test.kws[3].name}  \${a1}, \${a2} = MyParamLib.Parameters

Correct Error When Using Keyword From Same Library With Different Names Without Prefix
    Check Test Case  Correct Error When Using Keyword From Same Library With Different Names Without Prefix 1
    Check Test Case  Correct Error When Using Keyword From Same Library With Different Names Without Prefix 2
    Check Test Case  Correct Error When Using Keyword From Same Library With Different Names Without Prefix 3

Dynamic Library
    Check Test Case  Dynamic Library

Dynamic Java Library
    [Tags]  jybot
    Check Test Case  Dynamic Java Library

Global Scope
    Check Test Case  Global Scope 1.1
    Check Test Case  Global Scope 1.2
    Check Test Case  Global Scope 2.1
    Check Test Case  Global Scope 2.2

Test Suite Scope
    Check Test Case  Test Suite Scope 1.1
    Check Test Case  Test Suite Scope 1.2
    Check Test Case  Test Suite Scope 2.1
    Check Test Case  Test Suite Scope 2.2

Test Case Scope
    Check Test Case  Test Case Scope 1.1
    Check Test Case  Test Case Scope 1.2
    Check Test Case  Test Case Scope 2.1
    Check Test Case  Test Case Scope 2.2

With Name When Library Arguments Are Not Strings
    Check Syslog Contains  Imported library 'ParameterLibrary' with arguments [ 1 | 2 ]

*** Keywords ***
Run 'With Name' Tests
    Run Tests  ${EMPTY}  test_libraries/with_name_1.txt  test_libraries/with_name_2.txt  test_libraries/with_name_3.txt
    Should Be Equal  ${SUITE.name}  With Name 1 & With Name 2 & With Name 3

