*** Settings ***
Force Tags        regression    pybot    jybot
Resource          rebot_cli_resource.robot
Suite Setup       Run tests to create input file for Rebot
Test Template     Rebot Should Fail

*** Test Cases ***

Invalid Options
    --invalid option    option --invalid not recognized
    --name valid -I     option -I not recognized

No Input
    ${EMPTY}    Expected at least 1 argument, got 0.

Non-Existing Input
    nönéx.xml    Reading XML source 'nönéx\\.xml' failed: .*

Existing And Non-Existing Input
    ${MYINPUT} nönéx.xml nonex2.xml    Reading XML source 'nönéx\\.xml' failed: .*

Non-XML Input
    [Setup]    Create File    ${MYOUTDIR}/invalid.robot    Hello, world
    ${MYOUTDIR}${/}invalid.robot    (\\[Fatal Error\\] .*: Content is not allowed in prolog.\\n)?Reading XML source '.*invalid.robot' failed: .*

Incompatible XML
    [Setup]    Create File    ${MYOUTDIR}/invalid.xml    <not><our>type</our></not>
    ${MYOUTDIR}${/}invalid.xml    Reading XML source '.*invalid.xml' failed: Incompatible XML element 'not'.

Invalid Output Directory
    [Setup]    Create File    ${MYOUTDIR}${/}not-dir
    -d ${MYOUTDIR}${/}not-dir${/}dir ${MYINPUT}
    ...    Creating log file directory '.*' failed: .*
    -d ${MYOUTDIR}${/}not-dir${/}dir -o out.xml -l none -r none ${MYINPUT}
    ...    Creating output file directory '.*' failed: .*

Invalid --SuiteStatLevel
    --suitestatlevel not_int ${MYINPUT}
    ...    Option '--suitestatlevel' expected integer value but got 'not_int'.

Invalid --TagStatLink
    --tagstatlink a:b:c --TagStatLink less_than_3x_: ${MYINPUT}
    ...    Invalid format for option '--tagstatlink'. Expected 'tag:link:title' but got 'less_than_3x_:'.

Invalid --RemoveKeywords
    --removekeywords wuks --removek name:xxx --RemoveKeywords Invalid ${MYINPUT}
    ...    Invalid value for option '--removekeywords'. Expected 'ALL', 'PASSED', 'NAME:<pattern>', 'FOR', or 'WUKS' but got 'Invalid'.

*** Keywords ***

Rebot Should Fail
    [Arguments]    ${options}    ${exp msg}
    Set Runners
    ${rc}    ${output} =    Run And Return RC and Output    ${REBOT} ${options}
    Log    ${output}
    Should Be Equal As Integers    ${rc}    252
    Should Match Regexp    ${output}    ^\\[ .*ERROR.* \\] ${exp msg}${USAGETIP}$
