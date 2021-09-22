*** Settings ***
Test Setup      Create Output Directory
Resource        cli_resource.robot
Test Template   Run Should Fail

*** Test Cases ***
No Input
    ${EMPTY}    Expected at least 1 argument, got 0\\.

Argument File Option Without Value As Last Argument
    --argumentfile    option --argumentfile requires argument

Non-Existing Input
    nonexisting.robot    Parsing 'nonexisting\\.robot' failed: File or directory to execute does not exist\\.

Non-Existing Input With Non-Ascii Characters
    eitäällä.robot    Parsing 'eitäällä\\.robot' failed: File or directory to execute does not exist\\.

Invalid Output Directory
    [Setup]    Create File    %{TEMPDIR}/not-dir
    -d %{TEMPDIR}/not-dir/dir ${DATADIR}/${TEST FILE}
    ...    Creating output file directory '.*not-dir.dir' failed: .*
    -d %{TEMPDIR}/not-dir/dir -o %{TEMPDIR}/out.xml ${DATADIR}/${TEST FILE}
    ...    Creating report file directory '.*not-dir.dir' failed: .*

Invalid Options
    --invalid option    option --invalid not recognized
    --name valid -Q tests.robot    option -Q not recognized

Invalid --SuiteStatLevel
    --suitestatlevel not_int tests.robot
    ...  Option '--suitestatlevel' expected integer value but got 'not_int'.

Invalid --TagStatLink
    --tagstatlink a:b:c --TagStatLi less_than_3x_: tests.robot
    ...    Invalid format for option '--tagstatlink'. Expected 'tag:link:title' but got 'less_than_3x_:'.

Invalid --RemoveKeywords
    --removekeywords wuks --removek name:xxx --RemoveKeywords Invalid tests.robot
    ...    Invalid value for option '--removekeywords'. Expected 'ALL', 'PASSED', 'NAME:<pattern>', 'TAG:<pattern>', 'FOR', or 'WUKS' but got 'Invalid'.
