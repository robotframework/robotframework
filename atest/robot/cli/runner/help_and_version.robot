*** Settings ***
Resource          cli_resource.robot

*** Test Cases ***
Help
    ${result} =            Run Tests       --help    output=NONE
    Should Be Equal        ${result.rc}    ${251}
    Should Be Empty        ${result.stderr}
    ${help} =              Set Variable    ${result.stdout}
    Log                    ${help}
    Should Start With      ${help}         Robot Framework -- A generic automation framework\n\nVersion: \
    ${end} =               Catenate        SEPARATOR=\n
    ...    \# Setting default options and syslog file before running tests.
    ...    $ export ROBOT_OPTIONS="--outputdir results --suitestatlevel 2"
    ...    $ export ROBOT_SYSLOG_FILE=/tmp/syslog.txt
    ...    $ robot tests.robot
    Should End With        ${help}         \n\n${end}\n
    Should Not Contain     ${help}         \t
    Should Not Contain     ${help}         [ ERROR ]
    Should Not Contain     ${help}         [ WARN \ ]
    @{long} =              Evaluate        [line for line in $help.splitlines() if len(line) >= 80]
    Log Many               @{long}
    Should Be Empty        ${long}         Too long (>= 80) help line(s)
    @{tail} =              Evaluate        [repr(line) for line in $help.splitlines() if line != line.rstrip()]
    Log Many               @{tail}
    Should Be Empty        ${tail}         Help lines with trailing spaces

Version
    ${result} =    Run Tests    --version    output=NONE
    Should Be Equal        ${result.rc}    ${251}
    Should Be Empty        ${result.stderr}
    Should Match Regexp    ${result.stdout}
    ...    ^Robot Framework [567]\\.\\d(\\.\\d)?((a|b|rc)\\d)?(\\.dev\\d)? \\((Python|PyPy) 3\\.[\\d.]+.* on .+\\)$
    Should Be True         len($result.stdout) < 80    Too long version line
