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
    nonexisting.html    Parsing 'nonexisting\\.html' failed: Data source does not exist\\.

Non-Existing Input With Non-Ascii Characters
    eitäällä.txt    Parsing 'eitäällä\\.txt' failed: Data source does not exist\\.

Invalid Options
    --invalid option    option --invalid not recognized
    --name valid -X tests.txt    option -X not recognized

Invalid --SuiteStatLevel
    --suitestatlevel not_int tests.txt
    ...  Option '--suitestatlevel' expected integer value but got 'not_int'.

Invalid --TagStatLink
    --tagstatlink a:b:c --TagStatLi less_than_3x_: tests.txt
    ...    Invalid format for option '--tagstatlink'. Expected 'tag:link:title' but got 'less_than_3x_:'.

Invalid --RemoveKeywords
    --removekeywords wuks --removek name:xxx --RemoveKeywords Invalid tests.txt
    ...    Invalid value for option '--removekeywords'. Expected 'ALL', 'PASSED', 'NAME:<pattern>', 'FOR', or 'WUKS' but got 'Invalid'.
