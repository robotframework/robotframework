*** Settings ***
Resource           process_resource.robot

Test Setup    Start Interactive Python
Test Teardown    Terminate Process    ${PROCESS}

*** Variables ***
${PROCESS}    ${None}

*** Test Cases ***
Send Input To Process Default
    Send Input To Process    print('Hello')


Send Input To Process Without End Line
    Send Input To Process    print('Hello')    end_of_line=${None}
    Send Input To Process    \n    end_of_line=${None}

Read STDOUT
    Send Input To Process    print('Hello')
    ${stdout}    Read Output From Process
    Should Be Equal    ${stdout}    Hello

Read STDERR
    Send Input To Process    error
    ${stderr}    Read Output From Process    stream=stderr    lines=-1
    Should Contain    ${stderr}    NameError: name 'error' is not defined. Did you mean: 'OSError'?

Read Both Outputs
    Send Input To Process    print('Hello')
    Send Input To Process    error
    ${stdout}    ${stderr}    Read Output From Process    stream=both    lines=-1
    Should Be Equal    ${stdout}    Hello
    Should Contain    ${stderr}    NameError: name 'error' is not defined. Did you mean: 'OSError'?


Read Output From Process Default
    Send Input To Process    print('Hello')
    Process Output Should Contain    Hello

Read Output From Process stderr
    Send Input To Process    error
    Process Output Should Contain    NameError: name 'error' is not defined. Did you mean: 'OSError'?    stream=stderr    lines=-1


*** Keywords ***
Start Interactive Python
    ${PROCESS}    Run Python Process Interactive
    VAR    ${PROCESS}    ${PROCESS}    scope=TEST
