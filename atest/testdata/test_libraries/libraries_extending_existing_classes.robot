*** Settings ***
Library         ExtendPythonLib
Library         extendingjava.ExtendJavaLib

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

Keyword From Java Class Extended By Python Class
    [Documentation]  FAIL ArithmeticException: / by zero
    ${value} =  extendingjava.ExtendJavaLib.returnStringFromLibrary  Hello, world!
    Should Be Equal  ${value}  Hello, world!
    Div By Zero

Keyword From Python Class Extending Java Class
    ${value} =  kw_in_java_extender  ${2}
    Should Be Equal  ${value}  ${4}

Method In Python Class Overriding Method In Java Class
    [Documentation]  FAIL Overridden kw executed!
    Java Sleep  1

Keyword In Python Class Using Method From Java Class
    [Documentation]  FAIL ArithmeticException: / by zero
    Using Method From Java Parent

