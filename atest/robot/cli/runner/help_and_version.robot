*** Settings ***
Default Tags    regression  pybot  jybot
Resource        cli_resource.robot

*** Test Cases ***

Help
    Set Runners
    ${rc}  ${help} =  Run And Return Rc And Output  ${ROBOT} --help
    Should Be Equal  ${rc}  ${251}
    Log  ${help.replace(' ','_')}
    Should Not Contain  ${help}  \t
    Should Start With  ${help}  Robot Framework -- A generic test automation framework\n\nVersion: \
    ${end} =    Catenate    SEPARATOR=\n
    ...    \# Setting default options and syslog file before running tests.
    ...    $ export ROBOT_OPTIONS="--critical regression --suitestatlevel 2"
    ...    $ export ROBOT_SYSLOG_FILE=/tmp/syslog.txt
    ...    $ pybot tests.tsv
    Should End With    ${help}    \n\n${end}\n
    Should Not Contain  ${help}  [ ERROR ]
    Should Not Contain  ${help}  [ WARN \ ]
    @{lines} =  Evaluate  [ '%d\\t%s' % (len(line), line) for line in ${help.splitlines()} ]
    Log Many  @{lines}
    @{long} =  Evaluate  [ line for line in ${help.splitlines()} if len(line) - line.count('\\\\') >= 80 ]
    Log Many  @{long}
    Should Be True  len(@{long}) == 0  Too long (>= 80) help line(s)
    ${help2} =  Run  ${ROBOT} -h
    Should Be Equal  ${help}  ${help2}

Version
    Set Runners
    ${rc}  ${output} =  Run And Return Rc And Output  ${ROBOT} --version
    Should Be Equal  ${rc}  ${251}
    Log  ${output}
    Should Match Regexp  ${output}  ^Robot Framework 2\\.\\d+(\\.\\d+)?((a|b|rc|.dev)\\d+)? \\((Python|Jython|IronPython) [23]\\.[\\d.]+.* on .+\\)$
    Should Be True  len("${output}") < 80  Too long version line
