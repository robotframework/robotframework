*** Settings ***
Suite Setup       Run 'With Name' Tests
Resource          atest_resource.robot

*** Test Cases ***
Import Library Normally Before Importing With Name In Another Suite
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    OperatingSystem.Should Exist    args=.
    Check Keyword Data    ${tc.kws[1]}    ParameterLibrary.Parameters Should Be    args=before1, before2
    Syslog Should Contain    Imported library 'OperatingSystem' with arguments [ ] (version ${ROBOT VERSION}, class type, GLOBAL scope,
    Syslog Should Contain    Imported library 'ParameterLibrary' with arguments [ before1 | before2 ] (version <unknown>, class type, TEST scope,

Import Library With Name Before Importing With Name In Another Suite
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    Params.Parameters Should Be    args=before1with, before2with
    Syslog Should Contain    Imported library 'ParameterLibrary' with arguments [ after1 | after2 ] (version <unknown>, class type, TEST scope,

Import Library Normally After Importing With Name In Another Suite
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    OperatingSystem.Should Exist    args=.
    Check Keyword Data    ${tc.kws[1]}    ParameterLibrary.Parameters Should Be    args=after1, after2

Import Library With Name After Importing With Name In Another Suite
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    Params.Parameters Should Be    args=after1with, after2with

Name Given Using "With Name" Can Be Reused In Different Suites
    ${tc} =    Check Test Case    Import Library With Name Before Importing With Name In Another Suite
    Check Keyword Data    ${tc.kws[0]}    Params.Parameters Should Be    args=before1with, before2with
    ${tc} =    Check Test Case    Name Given Using "With Name" Can Be Reused in Different Suites
    Check Keyword Data    ${tc.kws[0]}    Params.Keyword In My Lib File
    Check Log Message    ${tc.kws[0].msgs[0]}    Here we go!!
    ${tc} =    Check Test Case    Import Library With Name After Importing With Name In Another Suite
    Check Keyword Data    ${tc.kws[0]}    Params.Parameters Should Be    args=after1with, after2with

No Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    OS.Directory Should Exist    args=.
    Check Keyword Data    ${tc.kws[1]}    OS.Should Exist    args=.
    Syslog Should Contain    Imported library 'OperatingSystem' with name 'OS'

Embedded Arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    arg
    Check Log Message    ${tc.kws[1].msgs[0]}    --args--

Embedded Arguments With Library Having State
    Check Test Case    ${TEST NAME}

Arguments Containing Variables And Import Same Library Twice
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    Param1.Parameters Should Be    args=1, 2
    Check Keyword Data    ${tc.kws[1]}    Param2.Parameters Should Be    args=VAR, \${42}
    Syslog Should Contain    Imported library 'ParameterLibrary' with arguments [ 1 | 2 ] (version <unknown>, class type, TEST scope,
    Syslog Should Contain    Imported library 'ParameterLibrary' with name 'Param1'
    Syslog Should Contain    Imported library 'ParameterLibrary' with arguments [ VAR | 42 ] (version <unknown>, class type, TEST scope,
    Syslog Should Contain    Imported library 'ParameterLibrary' with name 'Param2'

Alias Containing Variable
    Check Test Case    ${TEST NAME}

With Name Has No Effect If Not Second Last
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    ParameterLibrary.Parameters Should Be    args=whatever, WITH NAME
    Syslog Should Contain    Imported library 'ParameterLibrary' with arguments [ whatever | WITH NAME ] (version <unknown>, class type, TEST scope,

With Name After Normal Import
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    B2.Fail    args=This failure comes from B2!    status=FAIL
    Syslog Should Contain    Imported library 'BuiltIn' with name 'B2'

Module Library
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[0]}    MOD1.Argument    args=Hello
    Check Keyword Data    ${tc.kws[1]}    mod 2.Keyword From Submodule    \${s}    Tellus
    Check Keyword Data    ${tc.kws[3]}    MOD1.Failing    status=FAIL
    Syslog Should Contain    Imported library 'module_library' with name 'MOD1'
    Syslog Should Contain    Imported library 'pythonmodule.library' with name 'mod 2'

Import Library Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Keyword Data    ${tc.kws[1]}    MyOS.Directory Should Exist    args=.
    Check Keyword Data    ${tc.kws[3]}    MyParamLib.Parameters Should Be    args=my first argument, second arg

Correct Error When Using Keyword From Same Library With Different Names Without Prefix
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3

Dynamic Library
    Check Test Case    ${TEST NAME}

Global Scope
    Check Test Case    ${TEST NAME} 1.1
    Check Test Case    ${TEST NAME} 1.2
    Check Test Case    ${TEST NAME} 2.1
    Check Test Case    ${TEST NAME} 2.2

Test Suite Scope
    Check Test Case    ${TEST NAME} 1.1
    Check Test Case    ${TEST NAME} 1.2
    Check Test Case    ${TEST NAME} 2.1
    Check Test Case    ${TEST NAME} 2.2

Test Case Scope
    Check Test Case    ${TEST NAME} 1.1
    Check Test Case    ${TEST NAME} 1.2
    Check Test Case    ${TEST NAME} 2.1
    Check Test Case    ${TEST NAME} 2.2

With Name When Library Arguments Are Not Strings
    Syslog Should Contain    Imported library 'ParameterLibrary' with arguments [ 1 | 2 ]

'WITH NAME' is case-sensitive
    Error In File    -1    test_libraries/with_name_3.robot    5
    ...    Library 'ParameterLibrary' expected 0 to 2 arguments, got 4.

'WITH NAME' cannot come from variable
    Check Test Case    ${TEST NAME}

'WITH NAME' cannot come from variable with 'Import Library' keyword
    Check Test Case    ${TEST NAME}

'WITH NAME' cannot come from variable with 'Import Library' keyword even when list variable opened
    Check Test Case    ${TEST NAME}

*** Keywords ***
Run 'With Name' Tests
    ${sources} =    Catenate
    ...    test_libraries/with_name_1.robot
    ...    test_libraries/with_name_2.robot
    ...    test_libraries/with_name_3.robot
    ...    test_libraries/with_name_4.robot
    Run Tests    ${EMPTY}    ${sources}
    Should Be Equal    ${SUITE.name}    With Name 1 & With Name 2 & With Name 3 & With Name 4
