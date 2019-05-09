*** Settings ***
Test Setup      Create Output Directory
Resource        cli_resource.robot
Test Template   Run Should Fail

*** Test Cases ***
No Input
    [Tags]    no-standalone
    ${EMPTY}    Expected at least 1 argument, got 0\\.

Argument File Option Without Value As Last Argument
    --argumentfile    option --argumentfile requires argument

Non-Existing Input
    nonexisting.html    Parsing 'nonexisting\\.html' failed: File or directory to execute does not exist\\.

Non-Existing Input With Non-Ascii Characters
    eitäällä.txt    Parsing 'eitäällä\\.txt' failed: File or directory to execute does not exist\\.

Invalid Options
    --invalid option    option --invalid not recognized
    --name valid -Q tests.txt    option -Q not recognized

Invalid --SuiteStatLevel
    --suitestatlevel not_int tests.txt
    ...  Option '--suitestatlevel' expected integer value but got 'not_int'.

Invalid --TagStatLink
    --tagstatlink a:b:c --TagStatLi less_than_3x_: tests.txt
    ...    Invalid format for option '--tagstatlink'. Expected 'tag:link:title' but got 'less_than_3x_:'.

Invalid --RemoveKeywords
    --removekeywords wuks --removek name:xxx --RemoveKeywords Invalid tests.txt
    ...    Invalid value for option '--removekeywords'. Expected 'ALL', 'PASSED', 'NAME:<pattern>', 'TAG:<pattern>', 'FOR', or 'WUKS' but got 'Invalid'.

Deprecated --WarnOnSkipped
    [Template]    NONE
    Run Tests    --warnonskippedfiles    misc/pass_and_fail.robot
    Check Test Case    Pass
    Check Test Case    Fail
    ${msg} =    Catenate
    ...    Option '--warnonskippedfiles' is deprecated and has no effect.
    ...    Nowadays all skipped files are reported.
    Check Log Message    ${ERRORS[0]}   ${msg}    WARN
