*** Settings ***
Documentation   NO RIDE because it could change WITH NAME format.
Library         OperatingSystem  WITH NAME  OS
Library         ParameterLibrary  1  2  with name  Param1
Library         ParameterLibrary  ${VAR}  ${42}  WITH NAME  Param2
Library         ParameterLibrary  a  b  WITH NAME  ${VAR}
Library         ParameterLibrary  whatever  with name
Library         BuiltIn  With Name  B2
Library         module_library  with name  MOD1
Library         pythonmodule.library  With Name  mod 2
Library         Example Java Library  with name  Java Lib
Library         javapkg.JavaPackageExample  with name  Java Pkg
Library         MyLibFile.py  with name  Params
Library         RunKeywordLibrary  with name  dynamic
Library         RunKeywordLibraryJava  with name  dynamicJava
Library         libraryscope.Global  WITH NAME  G Scope
Library         libraryscope.Suite  WITH NAME  S Scope
Library         libraryscope.Test  WITH NAME  T Scope

*** Variables ***
${VAR}          VAR

*** Test Cases ***
No Arguments
    [Documentation]  FAIL No keyword with name 'OperatingSystem.Should Exist' found.
    OS.Directory Should Exist  ${CURDIR}
    Should Exist  ${CURDIR}
    OperatingSystem.Should Exist  ${CURDIR}

Embedded Arguments
    Keyword with embedded arg in MyLibFile
    Params.Keyword With Embedded --args-- in MyLibFile

Arguments Containing Variables And Import Same Library Twice
    ${a1}  ${a2} =  Param1.parameters
    BuiltIn.Should Be Equal  ${a1}  1
    BuiltIn.Should Be Equal  ${a2}  2
    ${a1}  ${a2} =  par am 2 . par A meter S
    BuiltIn.Should Be Equal  ${a1}  VAR
    BuiltIn.Should Be Equal  ${a2}  ${42}

Alias Containing Variable
    ${a1}  ${a2} =  VAR.parameters
    BuiltIn.Should Be Equal  ${a1}  a
    BuiltIn.Should Be Equal  ${a2}  b
    ${a1}  ${a2} =  Run Keyword  ${VAR}.parameters
    BuiltIn.Should Be Equal  ${a1}  a
    BuiltIn.Should Be Equal  ${a2}  b

With Name Has No Effect If Not Second Last
    ${a1}  ${a2} =  ParameterLibrary.parameters
    BuiltIn.Should Be Equal  ${a1}  whatever
    BuiltIn.Should Be Equal  ${a2}  with name

With Name After Normal Import
    [Documentation]  FAIL This failure comes from B2!
    B2.Fail  This failure comes from B2!

Module Library
    [Documentation]  FAIL This is a failing keyword from module library
    mod1.argument  Hello
    ${s} =  M O D 2 . keyword from sub module  Tellus
    BuiltIn.Should Be Equal  ${s}  Hello, Tellus!
    Failing

Java Library
    [Documentation]  FAIL No keyword with name 'Example Java Library.Get Java Object' found.
    ${s} =  returnStringFromLibrary  whatever
    BuiltIn.Should Be Equal  ${s}  whatever
    ${obj} =  Java Lib . Get Java Object  My Name
    BuiltIn.Should Be Equal  ${obj.name}  My Name
    ${arr} =  Java Lib. Get String Array  foo  bar
    BuiltIn.Should Be Equal  ${arr[0]}  foo
    Example Java Library.Get Java Object  This fails

Java Library In Package
    [Documentation]  FAIL No keyword with name 'javapkg.JavaPackageExample.whatever' found.
    ${s1} =  javapkg.returnvalue
    ${s2} =  Return Value  Returned string value
    BuiltIn.Should Be Equal  ${s1}  ${s2}
    javapkg.JavaPackageExample.whatever

Name Given Using "With Name" Can Be Reused In Different Suites
    Para MS.Keyword In My Lib File

Import Library Keyword
    BuiltIn.Import Library  Operating System  With Name  MyOS
    MyOS.Directory Should Exist  ${CURDIR}
    B2.Import Library  ParameterLibrary  my first argument  second arg  WITH NAME  MyParamLib
    ${a1}  ${a2} =  My Param Lib . Para Me Ters
    BuiltIn.Should Be Equal  ${a1}  my first argument
    BuiltIn.Should Be Equal  ${a2}  second arg

Correct Error When Using Keyword From Same Library With Different Names Without Prefix 2
    [Documentation]  FAIL Multiple keywords with name 'Parameters' found.\
    ...  Give the full name of the keyword you want to use:
    ...  ${SPACE*4}MyParamLib.Parameters
    ...  ${SPACE*4}Param1.Parameters
    ...  ${SPACE*4}Param2.Parameters
    ...  ${SPACE*4}ParameterLibrary.Parameters
    ...  ${SPACE*4}VAR.Parameters
    Parameters

Dynamic Library
    [Documentation]  FAIL No keyword with name 'RunKeywordLibrary.Run Keyword That Passes' found.
    dynamic.Run Keyword That Passes  arg1  arg2
    RunKeywordLibrary.Run Keyword That Passes

Dynamic Java Library
    [Documentation]  FAIL No keyword with name 'RunKeywordLibraryJava.Run Keyword That Passes' found.
    dynamicJava.Run Keyword That Passes  arg1  arg2
    RunKeywordLibraryJava.Run Keyword That Passes

Global Scope 2.1
    Register And Test Registered  G Scope  G.2.1  G.1.1  G.1.2

Global Scope 2.2
    Register And Test Registered  G Scope  G.2.2  G.1.1  G.1.2  G.2.1

Test Suite Scope 2.1
    Register And Test Registered  S Scope  S.2.1

Test Suite Scope 2.2
    Register And Test Registered  S Scope  S.2.2  S.2.1

Test Case Scope 2.1
    Register And Test Registered  T Scope  T.2.1

Test Case Scope 2.2
    Register And Test Registered  T Scope  T.2.2

*** Keywords ***
Register And Test Registered
    [Arguments]  ${scope}  ${reg}  @{exp}
    Run Keyword  ${scope}.Register  ${reg}
    Run Keyword  ${scope}.Should Be Registered  ${reg}  @{exp}
