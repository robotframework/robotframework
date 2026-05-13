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

Verbose with log and report
    Run Rebot    --console verbose --log log.html --report report.html    ${INPUT FILE}
    Stdout Should Contain    Output:
    Stdout Should Contain    Log:
    Stdout Should Contain    Report:

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

Custom console by path
    Run Rebot    --console ${CONSOLES}${/}CustomConsole.py --log log.html --report report.html
    ...    ${INPUT FILE}
    Stdout Should Contain    DEFAULT: Output:
    Stdout Should Contain    DEFAULT: Log:
    Stdout Should Contain    DEFAULT: Report:
    Stdout Should Contain    DEFAULT: Closing

Custom console by path with argument
    Run Rebot    --console ${CONSOLES}${/}CustomConsole.py:ARGUMENT --log log.html --report report.html
    ...    ${INPUT FILE}
    Stdout Should Contain    ARGUMENT: Output:
    Stdout Should Contain    ARGUMENT: Log:
    Stdout Should Contain    ARGUMENT: Report:
    Stdout Should Contain    ARGUMENT: Closing

Custom console by module name
    Run Rebot    --console CustomConsole --pythonpath ${CONSOLES} --log log.html --report report.html
    ...    ${INPUT FILE}
    Stdout Should Contain    DEFAULT: Output:
    Stdout Should Contain    DEFAULT: Closing

Custom console as module with functions
    Run Rebot    --console ${CONSOLES}${/}module_console.py    ${INPUT FILE}
    Stdout Should Not Contain    Output:
    Stdout Should Not Contain    Report:
    Stdout Should Not Contain    Log:
    Stdout Should Contain    MODULE: Closing

Non-existing custom console
    Run Rebot Without Processing Output    --console NonExistent    ${INPUT FILE}
    Stderr Should Start With    [ ERROR ] Taking console logger 'NonExistent' into use failed:

Dotted is not supported
    Run Rebot Without Processing Output    --console dotted    ${INPUT FILE}
    Stderr Should Be Equal To    [ ERROR ] Console type 'dotted' is not supported with Rebot.${USAGE TIP}\n
