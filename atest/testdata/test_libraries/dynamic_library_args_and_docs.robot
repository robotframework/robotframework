*** Settings ***
Library           classes.ArgDocDynamicLibrary
Library           classes.InvalidGetDocDynamicLibrary
Library           classes.InvalidGetArgsDynamicLibrary

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

Default value as tuple
    [Documentation]    FAIL Keyword 'classes.ArgDocDynamicLibrary.Default As Tuple' expected 1 to 3 arguments, got 4.
    Default as tuple    1
    Default as tuple    1    2
    Default as tuple    1    2    3
    Default as tuple    1    d2=3
    Default as tuple    1    FALSE    3
    Default as tuple    1    2    3    4

Documentation and Argument Boundaries Work With Varargs
    Many Args
    Many Args    1    2    3    4    5    6    7    8    9    10    11    12    13

Documentation and Argument Boundaries Work When Argspec is None
    No Arg Spec
    No Arg Spec    1    2    3    4    5    6    7    8    9    10    11    12    13

Multiline Documentation
    Multiline
