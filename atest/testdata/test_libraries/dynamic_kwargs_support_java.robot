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
    [Documentation]  FAIL Keyword 'ArgDocDynamicJavaLibraryWithKwargsSupport.Java Kwargs' expected 0 non-named arguments, got 1.
    Java Kwargs  key=value
    Java Kwargs  1

Documentation and Argument Boundaries Work With Varargs and Kwargs In Java
    Java Varargs and Kwargs  1  2  3  key=value

Only one runkeyword implementation
    ${ret} =    All arg types    hello   there   kitty   foo=whut
    Should Be Equal    ${ret}    All arg types: hello there kitty foo:whut

Default values
    ${ret} =    Defaults    only
    Should Be Equal    ${ret}    Defaults: only
    ${ret} =    Defaults    three    values    max
    Should Be Equal    ${ret}    Defaults: three values max

Named arguments
    ${ret} =    All arg types    arg=value
    Should Be Equal    ${ret}    All arg types: arg:value
    ${ret} =    Defaults    c=Z    a=X    b=Y
    Should Be Equal    ${ret}    Defaults: a:X b:Y c:Z
    ${ret} =    Defaults    b=only
    Should Be Equal    ${ret}    Defaults: b:only
