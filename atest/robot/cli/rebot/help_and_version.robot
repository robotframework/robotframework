*** Settings ***
Resource          rebot_cli_resource.robot

*** Test Cases ***
Help
    ${result} =            Run Rebot       --help    output=NONE
    Should Be Equal        ${result.rc}    ${251}
    Should Be Empty        ${result.stderr}
    ${help} =              Set Variable    ${result.stdout}
    Log                    ${help}
    Should Start With      ${help}         Rebot -- Robot Framework report and log generator\n\nVersion: \
    Should End With        ${help}         \n$ jython path/robot/rebot.py -N Project_X -l none -r x.html output.xml\n
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
    ${result} =            Run Rebot       --version    output=NONE
    Should Be Equal        ${result.rc}    ${251}
    Should Be Empty        ${result.stderr}
    Should Match Regexp    ${result.stdout}
    ...    ^Rebot [567]\\.\\d(\\.\\d)?((a|b|rc)\\d)?(\\.dev\\d)? \\((Python|PyPy) 3\\.[\\d.]+.* on .+\\)$
    Should Be True         len($result.stdout) < 80    Too long version line
