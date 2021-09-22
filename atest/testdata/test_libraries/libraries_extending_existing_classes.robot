*** Settings ***
Library         ExtendPythonLib

*** Test Cases ***
Keyword From Python Class Extended By Python Class
    [Documentation]  FAIL My error message
    Exception  AssertionError  My error message

Keyword From Python Class Extending Python Class
    ${value} =  kw_in_python_extender  ${4}
    Should Be Equal  ${value}  ${2}

Method In Python Class Overriding Method Of The Parent Class
    [Documentation]  FAIL Overridden kw executed!
    Print Many  Foo  bar  !

Keyword In Python Class Using Method From Parent Class
    [Documentation]  FAIL Error message from lib
    Using Method From Python Parent
