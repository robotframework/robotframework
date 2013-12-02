*** Settings ***
Library         RunKeywordLibraryJavaWithKwargsSupport
Library         ArgDocDynamicJavaLibraryWithKwargsSupport
Library         DynamicLibraryWithKwargsAndOnlyOneRunKeyword

*** Test Cases ***
Run Keyword
    Run Keyword That Passes
    ${ret} =  Run Keyword That Passes  Hi  tellus
    Should Be Equal  ${ret}  Hitellus
    ${ret} =  Run Keyword That Passes  Hi=tellus
    Should Be Equal  ${ret}  Hi:tellus
    ${ret} =  Run Keyword That Passes  Hi  tellus  some=more
    Should Be Equal  ${ret}  Hitellussome:more

Documentation and Argument Boundaries Work With Kwargs In Java
    [Documentation]  FAIL Keyword 'ArgDocDynamicJavaLibraryWithKwargsSupport.Java Kwargs' expected 0 non-keyword arguments, got 1.
    Java Kwargs  key=value
    Java Kwargs  1

Documentation and Argument Boundaries Work With Varargs and Kwargs In Java
    Java Varargs and Kwargs  1  2  3  key=value

Only one runkeyword implementation
    ${ret} =    All arg types    hello   there   kitty   foo=whut
    Should Be Equal    ${ret}    All arg types hello there kitty foo:whut
