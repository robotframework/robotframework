*** Settings ***
Resource          rebot_cli_resource.robot
Suite Setup       Run tests to create input file for Rebot    misc/pass_and_fail.robot    ${INPUT}
Test Template     Rebot Should Fail

*** Variables ***
${INPUT}          %{TEMPDIR}/input-for-cli-rebot-invalid-usage.xml

*** Test Cases ***
Invalid Options
    option --invalid not recognized    --invalid option
    option -I not recognized           --name valid -I

No Input
    Expected at least 1 argument, got 0.    source=

Non-Existing Input
    Reading XML source '.*nönéx.xml' failed: .*    source=nönéx.xml

Existing And Non-Existing Input
    Reading XML source '.*nönéx.xml' failed: .*    source=${INPUTFILE} nönéx.xml nonex2.xml

Non-XML Input
    [Setup]    Create File    %{TEMPDIR}/invalid.robot    Hello, world
    (\\[Fatal Error\\] .*: Content is not allowed in prolog.\\n)?Reading XML source '.*invalid.robot' failed: .*
    ...    source=%{TEMPDIR}/invalid.robot

Wrong XML root element
    [Setup]    Create File    %{TEMPDIR}/invalid.xml    <not><our>type</our></not>
    Reading XML source '.*invalid.xml' failed: Incompatible root element 'not'.
    ...    source=%{TEMPDIR}/invalid.xml

Wrong XML child element
    [Setup]    Create File    %{TEMPDIR}/invalid.xml    <robot><suite><test><wrong/></test></suite></robot>
    Reading XML source '.*invalid.xml' failed: Incompatible child element 'wrong' for 'test'.
    ...    source=%{TEMPDIR}/invalid.xml

Incompatible XML child element
    [Setup]    Create File    %{TEMPDIR}/invalid.xml    <robot><suite><test><test/></test></suite></robot>
    Reading XML source '.*invalid.xml' failed: Incompatible child element 'test' for 'test'.
    ...    source=%{TEMPDIR}/invalid.xml

Invalid Output Directory
    [Setup]    Create File    %{TEMPDIR}/not-dir
    Creating log file directory '.*not-dir.dir' failed: .*
    ...    -d %{TEMPDIR}/not-dir/dir
    Creating output file directory '.*not-dir.dir' failed: .*
    ...    -d %{TEMPDIR}/not-dir/dir -o out.xml -l none -r none

Invalid --SuiteStatLevel
    Option '--suitestatlevel' expected integer value but got 'not_int'.
    ...    --suitestatlevel not_int

Invalid --TagStatLink
    Invalid format for option '--tagstatlink'. Expected 'tag:link:title' but got 'less_than_3x_:'.
    ...    --tagstatlink a:b:c --TagStatLink less_than_3x_:

Invalid --RemoveKeywords
    Invalid value for option '--removekeywords'. Expected 'ALL', 'PASSED', 'NAME:<pattern>', 'TAG:<pattern>', 'FOR', or 'WUKS' but got 'Invalid'.
    ...    --removekeywords wuks --removek name:xxx --RemoveKeywords Invalid

--critical and --noncritical are deprecated
    [Template]    NONE
    ${result} =    Run Rebot    --critical pass --noncritical fail    ${INPUT}
    ${messsage} =    Catenate
    ...    Command line options --critical and --noncritical have been deprecated and have no effect with Rebot.
    ...    Use --skiponfailure when starting execution instead.
    Should Be Equal    ${result.stderr}    [ WARN ] ${messsage}
    Should Be Equal As Integers   ${result.rc}    1
    Check Test Case    Pass
    Check Test Case    Fail

*** Keywords ***
Rebot Should Fail
    [Arguments]    ${error}    ${options}=    ${source}=${INPUT}
    ${result} =    Run Rebot    ${options}    ${source}    default options=    output=
    Should Be Equal As Integers   ${result.rc}    252
    Should Be Empty    ${result.stdout}
    Should Match Regexp    ${result.stderr}    ^\\[ .*ERROR.* \\] ${error}${USAGETIP}$
