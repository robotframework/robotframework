*** Settings ***
Resource          cli_resource.robot

*** Test Cases ***
Help
    [Tags]    no-standalone
    ${result} =    Run Tests    --help    output=NONE
    Should Be Equal    ${result.rc}    ${251}
    Should Be Empty    ${result.stderr}
    Log    ${result.stdout.replace(' ','_')}
    Should Not Contain    ${result.stdout}    \t
    Should Start With    ${result.stdout}    Robot Framework -- A generic test automation framework\n\nVersion: \
    ${end} =    Catenate    SEPARATOR=\n
    ...    \# Setting default options and syslog file before running tests.
    ...    $ export ROBOT_OPTIONS="--critical regression --suitestatlevel 2"
    ...    $ export ROBOT_SYSLOG_FILE=/tmp/syslog.txt
    ...    $ pybot tests.tsv
    Should End With    ${result.stdout}    \n\n${end}\n
    Should Not Contain    ${result.stdout}    [ ERROR ]
    Should Not Contain    ${result.stdout}    [ WARN \ ]
    @{lines} =    Evaluate    [ '%d\\t%s' % (len(line), line) for line in $result.stdout.splitlines() ]
    Log Many    @{lines}
    @{long} =    Evaluate    [ line for line in $result.stdout.splitlines() if len(line) - line.count('\\\\') >= 80 ]
    Log Many    @{long}
    Should Be True    len(@{long}) == 0    Too long (>= 80) help line(s)

Version
    ${result} =    Run Tests    --version    output=NONE
    Should Be Equal    ${result.rc}    ${251}
    Should Be Empty    ${result.stderr}
    Should Match Regexp    ${result.stdout}    ^Robot Framework [23]\\.\\d+(\\.\\d+)?((a|b|rc|.dev)\\d+)? \\((Python|Jython|IronPython) [23]\\.[\\d.]+.* on .+\\)$
    Should Be True    len($result.stdout) < 80    Too long version line
