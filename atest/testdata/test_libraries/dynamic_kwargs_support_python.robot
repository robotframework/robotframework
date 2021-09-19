*** Settings ***
Library         dynamic_libraries/DynamicLibraryWithKwargsSupportWithoutArgspec.py
Library         classes.ArgDocDynamicLibraryWithKwargsSupport

*** Test Cases ***
Dynamic kwargs support should work without argument specification
    [Documentation]    PASS
    Do Something    print this
    Do Something else    something    something else
    Do Something else    something
    Do something third    x    b=1
    Do Something with kwargs    something    y=12    b=13

Unexpected keyword argument
    [Documentation]  FAIL GLOB: TypeError: *do_something_third() got an unexpected keyword argument 'y'
    Do something third    x    y=1

Documentation and Argument Boundaries Work With Kwargs
    [Documentation]  FAIL Keyword 'classes.ArgDocDynamicLibraryWithKwargsSupport.Kwargs' expected 0 non-named arguments, got 1.
    Kwargs  key=value
    Kwargs  1

Documentation and Argument Boundaries Work With Varargs and Kwargs
    Varargs and Kwargs
    Varargs and Kwargs  1  2  3
    Varargs and Kwargs  key=value
    Varargs and Kwargs  1  2  3  key=value

Documentation and Argument Boundaries Work When Argspec is None
    No Arg Spec
    No Arg Spec  1  2  3
    No Arg Spec  key=value
    No Arg Spec  1  2  3  key=value
