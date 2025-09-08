*** Settings ***
Resource          rebot_cli_resource.robot

*** Test Cases ***
---help
    ${result} =    Run Rebot    --help    output=NONE
    Validate --help    ${result}

--help --no-status-rc
    ${result} =    Run Rebot    --help --no-status-rc    output=NONE
    Validate --help    ${result}    rc=0

--version
    ${result} =    Run Rebot    --version    output=NONE
    Validate --version    ${result}

--version --no-status-rc
    ${result} =    Run Rebot    --VERSION --NoStatusRC    output=NONE
    Validate --version    ${result}    rc=0

*** Keywords ***
Validate --help
    [Arguments]    ${result}    ${rc}=251
    Should Be Equal        ${result.rc}    ${rc}    type=int
    Should Be Empty        ${result.stderr}
    VAR                    ${help}         ${result.stdout}
    Should Start With      ${help}         Rebot -- Robot Framework report and log generator\n\nVersion: \
    Should End With        ${help}         \n$ python -m robot.rebot --name Combined outputs/*.xml\n
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
    ...    ^Rebot [567]\\.\\d(\\.\\d)?((a|b|rc)\\d)?(\\.dev\\d)? \\((Python|PyPy) 3\\.[\\d.]+.* on .+\\)$
    Should Be True         len($result.stdout) < 80    Too long version line
