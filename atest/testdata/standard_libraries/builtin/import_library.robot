*** Test Cases ***

Import Library 1
    [Documentation]  Verify that keyword to be imported is not yet available FAIL No keyword with name 'Directory Should Exist' found.
    Directory Should Exist  ${CURDIR}

Import Library 2
    Import Library  OperatingSystem
    Directory Should Exist  ${CURDIR}

Import Library 3
    [Documentation]  Verify that keyword from lib imported by earlier kw is still available
    Directory Should Exist  ${CURDIR}

Import Library With Arguments
    Import Library  ParameterLibrary  value  nön-äscii
    ${first}  ${second} =  Parameters
    Should Be Equal  ${first}  value
    Should Be Equal  ${second}  nön-äscii

Import Library With Variables And WITH NAME
    ${name} =  Set Variable  ParameterLibrary
    Import Library  ${name}  ${42}  ${name}  WITH NAME  Variables-${42}
    ${first}  ${second} =  Variables-42.Parameters
    Should Be Equal  ${first}  ${42}
    Should Be Equal  ${second}  ParameterLibrary

Import Library Using Physical Path
    Import Library  ${CURDIR}${/}RegisteredClass.py
    RegisteredClass. Run Keyword If Method  False  Fail  This is not executed
    Import Library  ${CURDIR}/../../test_libraries/spaces in path/SpacePathLib.py
    ${ret} =  Spaces in Library Path
    Should Be Equal  ${ret}  here was a bug

Import Library Using Physical Path, Arguments And WITH NAME
    Import Library  ${CURDIR}/../../../testresources/testlibs/ParameterLibrary.py
    ...  first param  ${2}  WITH NAME  Params With Path
    ${params} =  Params With Path.Parameters
    Should Be True  ${params} == ('first param', 2)

Import Library Arguments Are Resolved Only Once
    ${var} =  Set Variable  \${not var}
    Import Library  ParameterLibrary  c:\\temp  ${var}  WITH NAME  Escaping
    ${first}  ${second} =  Escaping.Parameters
    Should Be Equal  ${first}  c:\\temp
    Should Be Equal  ${second}  \${not var}

Import Library With Named Arguments
    Import Library  ParameterLibrary  port=${2}  host=first  WITH NAME  Named
    ${first}  ${second} =  Named.Parameters
    Should Be Equal  ${first}  first
    Should Be Equal  ${second}  ${2}

Import Library Failure Is Catchable
    Run Keyword And Expect Error  Importing test library 'NonExistingLib' failed: ImportError: *
    ...  Import Library  NonExistingLib
