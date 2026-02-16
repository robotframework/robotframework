*** Settings ***
Resource          cli_resource.robot

*** Test Cases ***
---help
    ${result} =    Run Tests    --help    output=NONE
    Validate --help    ${result}

--help --no-status-rc
    ${result} =    Run Tests    --help --no-status-rc    output=NONE
    Validate --help    ${result}    rc=0

--version
    ${result} =    Run Tests    --version    output=NONE
    Validate --version    ${result}

--version --no-status-rc
    ${result} =    Run Tests    --VERSION --NoStatusRC    output=NONE
    Validate --version    ${result}    rc=0

*** Keywords ***
Validate --help
    [Arguments]    ${result}    ${rc}=251
    Should Be Equal        ${result.rc}    ${rc}    type=int
    Should Be Empty        ${result.stderr}
    VAR                    ${help}         ${result.stdout}
    Should Start With      ${help}         Robot Framework -- A generic automation framework\n\nVersion: \
    VAR                    ${end}
    ...    \# Setting default options and syslog file before running tests.
    ...    $ export ROBOT_OPTIONS="--outputdir results --suitestatlevel 2"
    ...    $ export ROBOT_SYSLOG_FILE=/tmp/syslog.txt
    ...    $ robot tests.robot
    ...    separator=\n
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

Validate --version
    [Arguments]    ${result}    ${rc}=251
    Should Be Equal        ${result.rc}    ${rc}    type=int
    Should Be Empty        ${result.stderr}
    Should Match Regexp    ${result.stdout}
    ...    ^Robot Framework [78]\\.\\d(\\.\\d)?((a|b|rc)\\d)?(\\.dev\\d)? \\((Python|PyPy) 3\\.[\\d.]+.* on .+\\)$
    Should Be True         len($result.stdout) < 80    Too long version line
