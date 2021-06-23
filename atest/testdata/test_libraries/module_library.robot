*** Settings ***
Library         module_library
Library         pythonmodule.library
Library         module_lib_with_all.py

*** Variables ***
@{INTS}  1  2  3  4  5  6  7
...  8  9  10

*** Test Cases ***
Passing
    Passing

Failing
    [Documentation]  FAIL This is a failing keyword from module library
    Failing

Logging
    Logging

Returning
    ${ret} =  Returning
    Should Be Equal  ${ret}  Hello from module library

One Argument
    [Documentation]  FAIL Expected 'Hello', got 'World'
    Argument  Hello
    Argument  World

Many Arguments
    [Documentation]  FAIL All arguments should have been equal, got: Hello, Hi and World
    Many Arguments  Hello  Hello  Hello
    Many Arguments  Hello  Hi  World

Default Arguments
    [Documentation]  FAIL All arguments should have been equal, got: Hello, Hi and Hello
    Default Arguments  Hello  Hello  Hello
    Default Arguments  Hello  Hello
    Default Arguments  Hello

Variable Arguments
    ${sum} =  Variable Arguments  2  3
    Should Be Equal  ${sum}  ${5}
    ${sum} =  Variable Arguments  @{INTS}
    Should Be Equal  ${sum}  ${55}

Only Methods And Functions Are Keywords
    [Documentation]  FAIL No keyword with name 'Attribute' found.
    Attribute

Class Methods In Module Library Are Not Keywords
    [Documentation]  FAIL STARTS: No keyword with name 'Not Keyword' found. Did you mean:
    Not Keyword

Functions starting with underscore are not keywords
    [Documentation]  FAIL STARTS: No keyword with name '_not_keyword' found. Did you mean:
    _not_keyword

If __all__ is present, only functions listed there are available 1
    [Documentation]  FAIL No keyword with name 'Not in all' found.
    ${path} =  Join with execdir  xxx
    Should Be Equal  ${path}  ${EXECDIR}${/}xxx
    ${path} =  Abspath  .
    Should Be Equal  ${path}  ${EXECDIR}
    Not in all

If __all__ is present, only functions listed there are available 2
    [Documentation]  FAIL No keyword with name 'Join' found.
    Join  arg1  arg2

If __all__ is present, only functions listed there are available 3
    [Documentation]  FAIL No keyword with name 'attr_is_not_kw' found.
    attr_is_not_kw

If __all__ is present, only functions listed there are available 4
    [Documentation]  FAIL No keyword with name '_not_kw_even_if_listed_in_all' found.
    _not_kw_even_if_listed_in_all

Class Method Assigned To Module Variable
    [Documentation]  FAIL Arguments should have been unequal, both were 'Hi'
    Two Arguments From Class  Hello  World
    Two Arguments From Class  Hi  Hi

Lambda Keyword
    [Documentation]  FAIL Keyword 'module_library.Lambda Keyword' expected 1 argument, got 2.
    ${ret} =  Lambda Keyword  2
    Should Be Equal  ${ret}  ${3}
    Lambda Keyword  2  3

Lambda Keyword With Arguments
    [Documentation]  FAIL STARTS: ZeroDivisionError:
    ${ret} =  Lambda Keyword With Two Args  4  2
    Should Be Equal  ${ret}  ${2}
    Lambda Keyword With Two Args  4  0

Attribute With Same Name As Module
    ${ret} =  module_library
    Should Be Equal  ${ret}  It should be OK to have an attribute with same name as the module

Importing Submodule As Library
    ${greeting} =  Keyword from submodule
    Should Be Equal  ${greeting}  Hello, World!
    ${greeting} =  Keyword from submodule  you
    Should Be Equal  ${greeting}  Hello, you!

