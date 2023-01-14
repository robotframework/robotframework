*** Settings ***
Test Setup      Create Output Directory
Resource        cli_resource.robot
Test Template   Run Should Fail

*** Variables ***
${VALID}        ${DATA DIR}/${TEST FILE}

*** Test Cases ***
No Input
    ${EMPTY}    Expected at least 1 argument, got 0.

Argument File Option Without Value As Last Argument
    --argumentfile    option --argumentfile requires argument

Non-Existing Input
    nonexisting.robot    Parsing '${EXECDIR}${/}nonexisting.robot' failed: File or directory to execute does not exist.

Non-Existing Input With Non-Ascii Characters
    nö.röböt ${VALID} bäd
    ...    Parsing '${EXECDIR}${/}nö.röböt' and '${EXECDIR}${/}bäd' failed: File or directory to execute does not exist.

Invalid Output Directory
    [Setup]    Create File    %{TEMPDIR}/not-dir
    -d %{TEMPDIR}/not-dir/dir ${VALID}
    ...    Creating output file directory '.*not-dir.dir' failed: .*    regexp=True
    -d %{TEMPDIR}/not-dir/dir -o %{TEMPDIR}/out.xml ${VALID}
    ...    Creating report file directory '.*not-dir.dir' failed: .*    regexp=True
    [Teardown]    Remove File    %{TEMPDIR}/not-dir

Invalid Options
    --invalid option    option --invalid not recognized
    --name valid -Q tests.robot    option -Q not recognized

Invalid --SuiteStatLevel
    --suitestatlevel not_int tests.robot
    ...    Invalid value for option '--suitestatlevel': Expected integer, got 'not_int'.

Invalid --TagStatLink
    --tagstatlink a:b:c --TagStatLi less_than_3x_: tests.robot
    ...    Invalid value for option '--tagstatlink': Expected format 'tag:link:title', got 'less_than_3x_:'.

Invalid --RemoveKeywords
    --removekeywords wuks --removek name:xxx --RemoveKeywords Invalid tests.robot
    ...    Invalid value for option '--removekeywords': Expected 'ALL', 'PASSED', 'NAME:<pattern>', 'TAG:<pattern>', 'FOR' or 'WUKS', got 'Invalid'.

Invalid --loglevel
    --loglevel bad tests.robot
    ...    Invalid value for option '--loglevel': Invalid level 'BAD'.
    --loglevel INFO:INV tests.robot
    ...    Invalid value for option '--loglevel': Invalid level 'INV'.
    -L INFO:DEBUG tests.robot
    ...    Invalid value for option '--loglevel': Level in log 'DEBUG' is lower than execution level 'INFO'.
