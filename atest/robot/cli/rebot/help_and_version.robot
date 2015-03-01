*** Settings ***
Test Setup      Empty Output Directory
Suite Setup     Set Runners
Force Tags      regression  pybot  jybot
Resource        atest_resource.robot
Resource        rebot_cli_resource.robot

*** Test Cases ***
Help
    ${rc}  ${help} =  Run And Return Rc And Output  ${REBOT} --help 2>&1
    Should Be Equal  ${rc}  ${251}
    Log  ${help.replace(' ','_').replace('\\t','_'*8)}
    Should Start With  ${help}  Rebot -- Robot Framework report and log generator\n\nVersion: \
    Should End With  ${help}  \n$ jython path/robot/rebot.py -N Project_X -l none -r x.html output.xml\n

    Should Not Contain  ${help}  ERROR
    @{lines} =  Evaluate  [ '%d\\t%s' % (len(line), line) for line in ${help.splitlines()} ]
    Log Many  @{lines}
    @{long} =  Evaluate  [ line for line in ${help.splitlines()} if len(line) - line.count('\\\\') >= 80 ]
    Log Many  @{long}
    Should Be True  len(@{long}) == 0  Too long (>= 80) help line(s)
    ${help2} =  Run  ${REBOT} -h 2>&1
    Should Be Equal  ${help}  ${help2}

Version
    ${rc}  ${output} =  Run And Return Rc And Output  ${REBOT} --version 2>&1
    Should Be Equal  ${rc}  ${251}
    Log  ${output}
    Should Match Regexp  ${output}  ^Rebot 2\\.\\d+(\\.\\d+)?((a|b|rc|.dev)\\d+)? \\((Python|Jython|IronPython) [23]\\.[\\d.]+.* on .+\\)$
    Should Be True  len("${output}") < 80  Too long version line
