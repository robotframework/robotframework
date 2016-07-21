*** Settings ***
Resource          rebot_cli_resource.robot

*** Test Cases ***
Help
    ${result} =    Run Rebot    --help    output=NONE
    Should Be Equal    ${result.rc}    ${251}
    Should Be Empty    ${result.stderr}
    ${help} =    Set variable    ${result.stdout}
    Log    ${help.replace(' ','_').replace('\\t','_'*8)}
    Should Start With    ${help}    Rebot -- Robot Framework report and log generator\n\nVersion: \
    Should End With    ${help}    \n$ jython path/robot/rebot.py -N Project_X -l none -r x.html output.xml\n
    Should Not Contain    ${help}    ERROR
    @{lines} =    Evaluate    [ '%d\\t%s' % (len(line), line) for line in $help.splitlines() ]
    Log Many    @{lines}
    @{long} =    Evaluate    [ line for line in $help.splitlines() if len(line) - line.count('\\\\') >= 80 ]
    Log Many    @{long}
    Should Be True    len($long) == 0    Too long (>= 80) help line(s)

Version
    ${result} =    Run Rebot    --version    output=NONE
    Should Be Equal    ${result.rc}    ${251}
    Should Be Empty    ${result.stderr}
    Should Match Regexp    ${result.stdout}    ^Rebot [23]\\.\\d+(\\.\\d+)?((a|b|rc|.dev)\\d+)? \\((Python|Jython|IronPython) [23]\\.[\\d.]+.* on .+\\)$
    Should Be True    len($result.stdout) < 80    Too long version line
