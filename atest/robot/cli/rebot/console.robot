*** Settings ***
Suite Setup       Run tests to create input file for Rebot
Resource          rebot_cli_resource.robot

*** Variables ***
${CONSOLES}       ${CURDIR}${/}..${/}..${/}..${/}testresources${/}consoles

*** Test Cases ***
Default is verbose
    Run Rebot    ${EMPTY}    ${INPUT FILE}
    Stdout Should Contain    Output:

Verbose
    Run Rebot    --console verbose    ${INPUT FILE}
    Stdout Should Contain    Output:

Quiet
    Run Rebot    --console quiet    ${INPUT FILE}
    Stdout Should Be Empty
    Stderr Should Be Empty

--quiet shortcut
    Run Rebot    --quiet    ${INPUT FILE}
    Stdout Should Be Empty
    Stderr Should Be Empty

None
    Run Rebot    --console none    ${INPUT FILE}
    Stdout Should Be Empty
    Stderr Should Be Empty

Custom console
    Run Rebot    --console CustomConsole --pythonpath ${CONSOLES} --log log.html --report report.html
    ...    ${INPUT FILE}
    Stdout Should Contain    DEFAULT: Output:
    Stdout Should Contain    DEFAULT: Closing

Non-existing custom console
    Run Rebot Without Processing Output    --console NonExistent    ${INPUT FILE}
    Stderr Should Start With    [ ERROR ] Taking console logger 'NonExistent' into use failed:
