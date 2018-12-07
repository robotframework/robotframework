*** Settings ***
Library           classes.ArgDocDynamicLibrary
Library           classes.InvalidGetDocDynamicLibrary
Library           classes.InvalidGetArgsDynamicLibrary
Library           ArgDocDynamicJavaLibrary

*** Test Cases ***
Documentation and Argument Boundaries Work With No Args
    [Documentation]    FAIL Keyword 'classes.ArgDocDynamicLibrary.No Arg' expected 0 arguments, got 1.
    No Arg
    No Arg    1

Documentation and Argument Boundaries Work With Mandatory Args
    [Documentation]    FAIL Keyword 'classes.ArgDocDynamicLibrary.One Arg' expected 1 argument, got 0.
    One Arg    arg
    One Arg

Documentation and Argument Boundaries Work With Default Args
    [Documentation]    FAIL Keyword 'classes.ArgDocDynamicLibrary.One Or Two Args' expected 1 to 2 arguments, got 3.
    One Or Two Args    1
    One Or Two Args    1    2
    One Or Two Args    1    2    3

Documentation and Argument Boundaries Work With Varargs
    Many Args
    Many Args    1    2    3    4    5    6    7    8    9    10    11    12    13

Documentation and Argument Boundaries Work When Argspec is None
    No Arg Spec
    No Arg Spec    1    2    3    4    5    6    7    8    9    10    11    12    13

Multiline Documentation
    Multiline

Documentation and Argument Boundaries Work With No Args In Java
    [Documentation]    FAIL Keyword 'ArgDocDynamicJavaLibrary.Java No Arg' expected 0 arguments, got 1.
    Java No Arg
    Java No Arg    foo

Documentation and Argument Boundaries Work With Mandatory Args In Java
    [Documentation]    FAIL Keyword 'ArgDocDynamicJavaLibrary.Java One Arg' expected 1 argument, got 0.
    Java One Arg    arg
    Java One Arg

Documentation and Argument Boundaries Work With Default Args In Java
    [Documentation]    FAIL Keyword 'ArgDocDynamicJavaLibrary.Java One Or Two Args' expected 1 to 2 arguments, got 3.
    Java One or Two Args    1
    Java One or Two Args    1    2
    Java One or Two Args    1    2    3

Documentation and Argument Boundaries Work With Varargs In Java
    Java Many Args
    Java Many Args    1    2    3    4    5    6    7    8    9    10    11    12    13
