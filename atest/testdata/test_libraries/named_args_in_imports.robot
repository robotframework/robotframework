*** Settings ***
Library  NamedArgsImportLibrary.py  arg2=value2  WITH NAME  NormalNamed
Library  NamedArgsImportLibrary.py  ${arg}  WITH NAME  NotNamed
Library  NamedArgsImportLibrary.py  arg2=${666}  WITH NAME  NonStringValue
Library  NamedArgsImportLibrary.py  @{ARGS}
Library  NamedArgsImportLibrary.py  kw1=arg1  kw2=arg2  kw3=arg3   WITH NAME   KwArgs


*** Variables ***
${ARG}   arg2=seppo
@{ARGS}  WITH NAME  NotWorks


*** Test Cases ***
Check kw arguments
    KwArgs.Check init arguments  ${null}  ${null}  kw1=arg1  kw2=arg2  kw3=arg3

Normal Named Arguments
    NormalNamed.Check Init Arguments  ${NONE}  value2

Non String Value
    NonStringValue.Check Init Arguments  ${NONE}  ${666}

Named Argument Syntax Doesn't Work Inside Variable
    NotNamed.Check Init Arguments  arg2\=seppo  ${NONE}

WITH NAME Doesn't Work Inside Variable
    [Documentation]  FAIL  No keyword with name 'NotWorks.Check Init Arguments' found.
    NamedArgsImportLibrary.Check Init Arguments  WITH NAME  NotWorks
    NotWorks.Check Init Arguments  ${NONE}  ${NONE}
